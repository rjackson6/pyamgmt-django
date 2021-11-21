/*jshint esversion: 6*/

/** Deform module for Django Forms
 *
 * @type {{buildWidgets: buildWidgets, buildForm: buildForm}}
 */

const DEFORM = (function(){
    // TODO: write to native JS to remove a dependency on jQuery, if it's not strictly necessary
    'use strict';

    /*
    templates/django/forms/widgets/attrs.html
    for name, value in widget.attrs.items
    if value is not False -> {{name}}
    if value is not True -> ="value|stringformat:'s'"
    endif endif endfor
     */

    /*
    templates/django/forms/widgets/input.html
    <input type="{{ widget.type}}" name="{{ widget.name }}"{% if widget.value != None %} value="{{ widget.value|stringformat:'s' }}"{% endif %}{% include django/forms/widgets/attrs.html %}>
     */

    /*
    templates/django/forms/wigdets/select.html
    <select name="{{ widget.name}}" {% include django/forms/widgets/attrs.html %}
    {% for group_name, group_choices, group_index in widget.optgroups %}
    {% if group_name %}<optgroup label="{{ group_name }}"{% endif %}
    {% for option in group_choices %}
    {% include option.template_name with widget=option %}
    {% endfor %}
    {% if group_name %}</optgroup>{% endif %}
    {% endfor %}
    </select>
     */

    /* <textarea name="{{ widget.name }}"{% include "django/forms/widgets/attrs.html" %}>
{% if widget.value %}{{ widget.value }}{% endif %}</textarea>
     */

    const buildAttrs = function buildAttrs($elm, attrs){
        // Ref: django/forms/widgets/attrs.html
        for (const [key, value] of Object.entries(attrs)) {
            if (key === 'class') {
                $elm.attr(key, value.join(" "));
            }
            else if (value !== false) {
                if (value !== true) {
                    $elm.attr(key, value);
                } else {
                    // Probably a boolean attribute, which works nicer with $.prop
                    $elm.prop(key, value);
                }
            }
        }
    };

    const buildCheckbox = function buildCheckbox(widget){
        // --> buildInput
        console.log('buildCheckbox');
        return buildInput(widget);
    };

    const buildCheckboxOption = function buildCheckboxOption(widget){
        // --> buildInputOption
        throw 'Not implemented';
    };

    const buildCheckboxSelect = function buildCheckboxSelect(widget){
        // --> buildMultipleInput
        throw 'Not implemented';
    };

    const buildDate = function buildDate(widget){
        // --> buildInput
        console.log('buildDate');
        return buildInput(widget);
    };

    const buildDateTime = function buildDateTime(widget){
        // --> buildInput
        throw 'Not implemented';
    };

    const buildEmail = function buildEmail(widget){
        // --> buildInput
        throw 'Not implemented';
    };

    const buildFile = function buildFile(widget){
        // --> buildInput
        throw 'Not implemented';
    };

    const buildHidden = function buildHidden(widget) {
        // Ref: django/forms/widgets/hidden.html
        console.log('buildHidden');
        return buildInput(widget);
    };

    const buildInput = function buildInput(widget){
        // Ref: django/forms/widgets/input.html
        console.log('buildInput');
        let $field = $('<input>').attr({
            type: widget.type,
            name: widget.name
        });
        buildAttrs($field, widget.attrs);
        if (widget.value) {
            $field.attr('value', widget.value);
            $field.val(widget.value);
        }
        return $field;
    };

    const buildInputOption = function buildInputOption(widget){
        // Ref: django/forms/widgets/input_option.html
        // Checks widget.wrap_label; includes a label tag
        // Includes template for input.html
        /*
        {% if widget.wrap_label %}
        <label
        {% if widget.attrs.id %} for="{{ widget.attrs.id }}"{% endif %}
        >{% endif %}
        {% include "django/forms/widgets/input.html" %}
        {% if widget.wrap_label %}
         {{ widget.label }}</label>
        {% endif %}
        */
        throw 'buildInputOption not implemented';
    };

    const buildMultiwidget = function buildMultiwidget(widget){
        // Ref: django/forms/widgets/multiwidget.html
        // iterates widget.subwidgets; include widget.template_name
        for (let i = 0; i < widget.subwidgets.length; i++) {
            buildWidget(widget.subwidgets[i]);
        }
        throw 'buildMultiWidget not fully implemented';
    };

    const buildNumber = function buildNumber(widget){
        // Ref: django/forms/widgets/number.html
        console.log('buildNumber');
        return buildInput(widget);
    };

    const buildSelect = function buildSelect(widget){
        // Ref: django/forms/widgets/select.html
        // + django/forms/widgets/select_option.html
        console.log('buildSelect');
        let $field = $('<select></select>').attr({
            name: widget.name
        });
        buildAttrs($field, widget.attrs);
        for (let i = 0; i < widget.optgroups.length; i++) {
            let $target = $field;
            let group_name = widget.optgroups[i][0];
            let group_choices = widget.optgroups[i][1];
            let group_index = widget.optgroups[i][2];
            if (group_name) {
                let $optgroup = $('<optgroup></optgroup>').attr('label', group_name);
                $target = $optgroup;
            }
            for (let j = 0; j < group_choices.length; j++) {
                let option = group_choices[j];
                $target.append(buildSelectOption(option));
            }
        }
        return $field;
    };

    const buildSelectDate = function buildSelectDate(widget){
        // --> multiwidget.hmtl
        throw 'buildSelectDate not implemented';
    };

    const buildSelectOption = function buildSelectOption(option){
        console.log('buildSelectOption');
        let $option = $('<option></option>').attr('value', option.value);
        buildAttrs($option, option.attrs);
        $option.text(option.label);
        return $option;
    };

    const buildText = function buildText(widget){
        console.log('buildText');
        return buildInput(widget);
    };

    const buildTime = function buildTime(widget){
        return buildInput(widget)
    };

    const buildWidget = function buildWidget(widget){
        console.log('--buildWidget');
        let djangoTemplate = widget.template_name;
        // retval / break / return retval is an alternative writing style
        switch (djangoTemplate) {
            case 'django/forms/widgets/checkbox.html':
                return buildCheckbox(widget);
            case 'django/forms/widgets/date.html':
                return buildDate(widget);
            case 'django/forms/widgets/hidden.html':
                return buildHidden(widget);
            case 'django/forms/widgets/number.html':
                return buildNumber(widget);
            case 'django/forms/widgets/select.html':
                return buildSelect(widget);
            case 'django/forms/widgets/text.html':
                return buildText(widget);
            case 'django/forms/widgets/time.html':
                return buildTime(widget);
        }
    };

    // TODO: "fields" refers more to a "form" right now, but I'm not sure how to structure it yet.
    const buildWidgets = function buildWidgets(fields){
        for (let i = 0; i < fields.length; i++) {
            let field = fields[i];
            console.log(field);
        }
        for (const [field_key, field_values] of Object.entries(fields)) {
            // console.log(field_key, field_values);
            for (let i = 0; i < field_values.length; i++) {
                let widget = field_values[i];
                // console.log(widget);
                $('#content').append(buildWidget(widget)); // TODO: should target a <form> element
            }
            //let widget = field_values.widget;
            // $('#content').append(buildWidget(widget)); // TODO: should target a <form> element
        }
    };

    const buildLabel = function buildLabel(label) {
        let $label = $('<label></label>');
        buildAttrs($label, label.attrs);
        $label.text(label.text);
        return $label;
    };

    const buildFieldErrors = function buildFieldErrors(errors) {
        let $errors = $('<ul></ul>');
        for (let i = 0; i < errors.length; i++) {
            $errors.append($('<li></li>').text(errors[i]));
        }
        return $errors;
    };

    const buildHelpText = function buildHelpText(help_text) {
        let $help_text = $('<span></span>')
            .text(help_text)
            .attr('class', 'helptext')  // TODO
        ;
        return $help_text;
    };

    const buildField = function buildField(field) {
        console.log('-buildField');
        let wrap_field = true;
        let wrap_label = false;
        let elms = [];
        // buildLabel
        let $label = buildLabel(field.label);
        if (wrap_label) {
            $label.append(buildWidget(field.field));
            elms.push($label);
        } else {
            elms.push($label);
            if (field.errors.length > 0) {  // TODO: rework this if block
               elms.push(buildFieldErrors(field.errors));
            }
            elms.push(buildWidget(field.field));
        }
        // buildWidget
        // buildInitialWidget
        // buildHelpText
        if (field.help_text) {
            elms.push(buildHelpText(field.help_text));
        }
        if (field.initial_field) {
            // No label or help_text; append it last like Django does for the sake of parity.
            elms.push(buildWidget(field.initial_field));
        }
        if (wrap_field) {
            let $field = $('<div></div>').attr('class', 'field-wrapper');
            $field.append(elms)
            return $field;
        }
        return elms;
    };

    const buildFormErrors = function buildFormErrors(form_errors) {
        let $error_div = $('<div></div>');
        for (let i = 0; i < form_errors.length; i++) {
            $error_div.append($('<p></p>').text(form_errors[i]));
        }
        return $error_div;
    };

    const buildForm = function buildForm(form_elm, form_data){
        // TODO: I think I do want to use field wrappers instead of defaults.
        console.log('buildForm');
        let $form = $(form_elm)
        // Form-level errors, fields, hidden_fields
        // buildFormErrors
        if (form_data.errors.length > 0) {
            console.log('form-level errors exist');
            $form.append(buildFormErrors(form_data.errors));
        }
        // buildFields
        for (let i = 0; i < form_data.fields.length; i++) {
            // buildWidgets(form_data.fields[i]);
            let field_data = form_data.fields[i];
            $form.append(buildField(field_data));
        }
        // buildHiddenFields
        for (let i = 0; i < form_data.hidden_fields.length; i++) {
            // TODO: create container for the hidden fields
            let field_data = form_data.hidden_fields[i];
            $form.append(buildHidden(field_data));
        }
        // TODO: CSRF?
    };

    const parseForm = function parseForm(elm, data) {
        // Formset or form
        let $form = $(elm);
        if ("management_form" && "forms" in data) {
            // build a FormSet
            console.log('detected formset');
            buildForm(elm, data.management_form);
            for (let i = 0; i < data.forms.length; i++) {
                buildForm(elm, data.forms[i]);
            }
        } else if ("fields" && "errors" in data) {
            console.log('detected form');
            buildForm(elm, data);
        }
        // Optional: add submit button
        let $btn_submit = $('<button></button>')
            .attr({
                'type': 'submit'
            })
            .text('Submit');
        $form.append($btn_submit);
    };

    // Two options: one parses formsets, one parses forms
    // Formset should have keys "management_form" and "forms"
    // A single form would just have "fields", "errors", etc.

    return {
        buildWidgets: buildWidgets,
        buildForm: buildForm,
        parseForm: parseForm
    }
}());
