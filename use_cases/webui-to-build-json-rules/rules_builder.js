$(function() { // Document Ready

    // --- Configuration ---
    const sortableOptions = {
        connectWith: ".connected-sortable", // Allows connecting lists
        placeholder: "ui-sortable-placeholder", // Class for placeholder visuals
        forcePlaceholderSize: true,
        // handle: ".drag-handle", // Optional: If you want specific drag handles
        tolerance: "pointer", // How close the cursor needs to be to trigger sorting
        revert: 100, // Animation duration on invalid drop
        helper: 'clone', // Clone item when dragging from palette
        // Event when item received from another list
        receive: function(event, ui) {
             const $item = $(ui.item);
             const $list = $(this); // The list receiving the item
             const itemType = $item.data('type');

             // Clone the received item and make it the real item (not the helper)
             const $newItem = $item.clone();
                $newItem.removeClass('list-group-item'); // Remove palette specific class if any
                $newItem.css('display', ''); // Ensure it's visible if cloned from template

             // Add remove button
             if (! $newItem.find('.delete-item').length) {
                 $newItem.append(' <button type="button" class="btn-close delete-item float-end" aria-label="Close"></button>');
             }

             // Special handling for condition groups
             if (itemType === 'group') {
                 const logic = $item.data('logic');
                 const $groupTemplate = $('#condition-group-template').clone().removeAttr('id').css('display', '');
                 $groupTemplate.data('logic', logic);
                 $groupTemplate.find('.logic-toggle').text(logic.toUpperCase());
                 $groupTemplate.find('.toggle-logic-btn').text(logic === 'all' ? 'Switch to ANY' : 'Switch to ALL');

                 // Replace the dropped placeholder item with the full group structure
                 ui.item.replaceWith($groupTemplate); // Replace original dragged item
                 makeListSortable($groupTemplate.find('.condition-group-list')); // Make the new list sortable
             } else {
                  // For conditions/actions, replace the helper/original item with the prepared clone
                  ui.item.replaceWith($newItem);
             }

             // If dragging from palette, remove original helper from palette (not needed with helper:'clone')
             // if (ui.sender && $(ui.sender).closest('.palette').length) {
             //   // It came from the palette
             // }

             makeListSortable($list); // Ensure list stays sortable if needed
        },
        // Event when sorting stops (within list or between lists)
        stop: function(event, ui) {
            // If item came from palette, remove the list-group-item class
             if (ui.item.data('original-list') === 'palette') {
                 ui.item.removeClass('list-group-item');
                 ui.item.removeData('original-list'); // Clean up marker
             }
        },
         // Event when sorting starts
         start: function(event, ui) {
             // Mark items dragged from palette
             if ($(this).closest('.palette').length) {
                 ui.item.data('original-list', 'palette');
             }
         }

    };

    // --- Initialization ---

    // Make palette items draggable (using sortable's connectWith)
    $(".palette-conditions, .palette-groups, .palette-actions").sortable({
        ...sortableOptions,
        connectWith: ".rules-canvas, .condition-group-list, .actions-list" // Where palette items can go
    }).disableSelection(); // Prevent text selection while dragging


    // Function to make a list sortable (used for dynamically added lists)
    function makeListSortable($list) {
        if (!$list.hasClass("ui-sortable")) {
            $list.sortable({
                ...sortableOptions,
                 helper: 'original', // Don't clone when reordering existing items
                 connectWith: ".condition-group-list, .actions-list" // Allow moving between compatible lists
            }).disableSelection();
        }
    }


    // --- Event Handlers ---

    // Add New Rule
    $('#add-rule-btn').on('click', function() {
        const $newRule = $('#rule-template').clone().removeAttr('id').css('display', '');
        $('#rules-canvas').append($newRule);
        // Make the new condition and action lists sortable
        makeListSortable($newRule.find('.condition-group-list'));
        makeListSortable($newRule.find('.actions-list'));
    });

    // Delete Rule / Item / Group (using event delegation)
    $('#rules-canvas').on('click', '.delete-rule', function() {
        $(this).closest('.rule-card').remove();
    });
    $('#rules-canvas').on('click', '.delete-item', function() {
        $(this).closest('.draggable-item, .condition-group').remove(); // Remove item or whole group
    });

    // Toggle Logic (ALL/ANY) for Condition Groups
    $('#rules-canvas').on('click', '.toggle-logic-btn', function() {
        const $button = $(this);
        const $group = $button.closest('.condition-group');
        const $toggleText = $group.find('.logic-toggle');
        const currentLogic = $group.data('logic');

        if (currentLogic === 'all') {
            $group.data('logic', 'any');
            $toggleText.text('ANY');
            $button.text('Switch to ALL');
        } else {
            $group.data('logic', 'all');
            $toggleText.text('ALL');
            $button.text('Switch to ANY');
        }
    });


    // --- JSON Generation ---

    $('#generate-json-btn').on('click', function() {
        const rules = [];
        $('#rules-canvas .rule-card').each(function() {
            const $ruleCard = $(this);
            const rule = {
                conditions: parseConditions($ruleCard.find('.card-body > .condition-group').first()), // Start parsing from the top-level group
                actions: []
            };

            // Parse Actions
            $ruleCard.find('.actions-list .draggable-item[data-type="action"]').each(function() {
                const $actionItem = $(this);
                const action = {
                    name: $actionItem.data('name'),
                    params: {}
                };
                let hasParams = false;
                $actionItem.find('.param-input').each(function() {
                    const $paramInput = $(this);
                    const paramName = $paramInput.data('param-name');
                    let paramValue = $paramInput.val();
                    // Attempt to convert numbers
                    if (paramValue !== "" && !isNaN(paramValue)) {
                         paramValue = Number(paramValue);
                    }
                    if (paramName && paramValue !== "") { // Only add param if name and value exist
                        action.params[paramName] = paramValue;
                        hasParams = true;
                    }
                });
                 if (!hasParams) {
                     delete action.params; // Remove params key if empty
                 }
                rule.actions.push(action);
            });

            rules.push(rule);
        });

        $('#json-output').text(JSON.stringify(rules, null, 2)); // Pretty print JSON
    });

    // Recursive function to parse conditions
    function parseConditions($groupElement) {
        if (!$groupElement || $groupElement.length === 0) {
            // Handle case where the initial group might have been deleted
            return { all: [] }; // Return a default empty structure
        }
        const logic = $groupElement.data('logic'); // 'all' or 'any'
        const conditions = [];

        // Find direct children: conditions or nested groups within this group's list
        $groupElement.find('> .condition-group-list > .draggable-item[data-type="condition"], > .condition-group-list > .condition-group').each(function() {
            const $element = $(this);

            if ($element.hasClass('condition-group')) {
                // Nested group: Recursively parse
                conditions.push(parseConditions($element));
            } else if ($element.data('type') === 'condition') {
                // Individual condition
                const valueInput = $element.find('.value-input');
                let value = valueInput.val();
                 // Attempt to convert numbers
                 if (value !== "" && !isNaN(value) && valueInput.attr('type') === 'number') {
                     value = Number(value);
                 }
                 // Only add if value is present (or operator doesn't need one?) - adjust if needed
                // if (value !== "" || ["exists", "does_not_exist"].includes($element.data('operator'))) { // Example: operators that might not need a value
                 if (value !== "") {
                    conditions.push({
                        name: $element.data('name'),
                        operator: $element.data('operator'),
                        value: value
                    });
                 }
            }
        });

        const result = {};
        result[logic] = conditions;
        return result;
    }

}); // End Document Ready