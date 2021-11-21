/*jshint esversion: 6*/

/**
 *
 * @type {{parseForm: parseForm}}
 */

const DEFORM = (function(){
    'use strict';

    const buildAttrs = function buildAttrs(elm, attrs){
        // Build widget attributes
        // Ref: django/forms/widgets/attrs.html
        console.debug('buildAttrs');
        for (const [key, value] of Object.entries(attrs)) {
            if (key === 'class') {
                elm.setAttribute(key, value.join(" "));
            }
            else if (value !== false) {
                elm.setAttribute(key, value);
            }
        }
    };

    const buildCheckbox = function buildCheckbox(widget){
        // --> buildInput
        console.debug('buildCheckbox');
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
        console.debug('buildDate');
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
        console.debug('buildHidden');
        return buildInput(widget);
    };

    /**
     *
     * @param widget
     * @returns {HTMLInputElement}
     */
    const buildInput = function buildInput(widget){
        // Ref: django/forms/widgets/input.html
        console.debug('buildInput');
        let input_elm = document.createElement("input");
        input_elm.setAttribute("type", widget.type);
        input_elm.setAttribute("name", widget.name);
        buildAttrs(input_elm, widget.attrs);
        if (widget.value) {
            input_elm.setAttribute("value", widget.value);
            // val? value?
        }
        return input_elm;
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

    /**
     *
     * @param widget
     * @returns {HTMLInputElement}
     */
    const buildNumber = function buildNumber(widget){
        // Ref: django/forms/widgets/number.html
        console.debug('buildNumber');
        return buildInput(widget);
    };

    const buildSelect = function buildSelect(widget){
        // Ref: django/forms/widgets/select.html
        // + django/forms/widgets/select_option.html
        console.debug('buildSelect');
        let select_elm = document.createElement("select");
        select_elm.setAttribute("name", widget.name);
        buildAttrs(select_elm, widget.attrs);
        for (let i = 0; i < widget.optgroups.length; i++) {
            let target = select_elm;
            let group_name = widget.optgroups[i][0];
            let group_choices = widget.optgroups[i][1];
            let group_index = widget.optgroups[i][2];
            if (group_name) {
                let optgroup = document.createElement("optgroup");
                optgroup.setAttribute("label", group_name);
                target = optgroup;
            }
            for (let j = 0; j < group_choices.length; j++) {
                let option = group_choices[j];
                target.append(buildSelectOption(option));
            }
        }
        return select_elm;
    };

    const buildSelectDate = function buildSelectDate(widget){
        // --> multiwidget.hmtl
        throw 'buildSelectDate not implemented';
    };

    const buildSelectOption = function buildSelectOption(option){
        console.debug('buildSelectOption');
        let option_elm = document.createElement("option");
        option_elm.setAttribute("value", option.value);
        buildAttrs(option_elm, option.attrs);
        option_elm.textContent = option.label;
        return option_elm;
    };

    const buildText = function buildText(widget){
        console.debug('buildText');
        return buildInput(widget);
    };

    const buildTextArea = function buildTextArea(widget){
        console.debug('buildTextArea');
          let textarea_elm = document.createElement("textarea");
          textarea_elm.setAttribute("name", widget.name);
          buildAttrs(textarea_elm, widget.attrs);
          textarea_elm.textContent = widget.value;
          return textarea_elm;
    };

    const buildTime = function buildTime(widget){
        console.debug('buildTime');
        return buildInput(widget)
    };

    const buildWidget = function buildWidget(widget){
        console.debug('--buildWidget');
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
            case 'django/forms/widgets/textarea.html':
                return buildTextArea(widget);
            case 'django/forms/widgets/time.html':
                return buildTime(widget);
            default:
                throw 'No template found to build form;';
        }
    };

    // TODO: "fields" refers more to a "form" right now, but I'm not sure how to structure it yet.
    const buildWidgets = function buildWidgets(fields){
        for (let i = 0; i < fields.length; i++) {
            let field = fields[i];
        }
        for (const [field_key, field_values] of Object.entries(fields)) {
            // console.log(field_key, field_values);
            for (let i = 0; i < field_values.length; i++) {
                let widget = field_values[i];
                // console.log(widget);
                // $('#content').append(buildWidget(widget)); // TODO: should target a <form> element
            }
            //let widget = field_values.widget;
            // $('#content').append(buildWidget(widget)); // TODO: should target a <form> element
        }
    };

    /**
     *
     * @param label
     * @returns {HTMLLabelElement}
     */
    const buildLabel = function buildLabel(label) {
        console.debug('buildLabel');
        let label_elm = document.createElement("label");
        buildAttrs(label_elm, label.attrs);
        label_elm.textContent = label.text;
        return label_elm;
    };

    const buildFieldErrors = function buildFieldErrors(errors) {
        console.debug('buildFieldErrors');
        let errors_ul = document.createElement("ul");
        for (let i = 0; i < errors.length; i++) {
            let errors_li = document.createElement("li");
            errors_li.textContent = errors[i];
            errors_ul.append(errors_li);
        }
        return errors_ul;
    };

    const buildHelpText = function buildHelpText(help_text) {
        console.debug('buildHelpText');
        let help_text_span = document.createElement("span");
        help_text_span.setAttribute("class", "helptext");
        help_text_span.textContent = help_text;
        return help_text_span;
    };

    /**
     *
     * @param field
     * @returns {HTMLDivElement|*[]}
     */
    const buildField = function buildField(field) {
        console.debug('-buildField');
        let wrap_field = true;
        let wrap_label = false;
        let elms = [];
        // buildLabel
        let label = buildLabel(field.label);
        if (wrap_label) {
            label.append(buildWidget(field.field));
            elms.push(label);
        } else {
            elms.push(label);
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
        if (field.initial_field.keys) {  // TODO: keys?
            // No label or help_text; append it last like Django does for the sake of parity.
            elms.push(buildWidget(field.initial_field));
        }
        if (wrap_field) {
            let field_div = document.createElement("div");
            field_div.setAttribute("class", "field-wrapper");
            for (let i = 0; i < elms.length; i++) {
                field_div.append(elms[i]);
            }
            // field_div.append(elms)
            return field_div;
        }
        return elms;
    };

    const buildFormErrors = function buildFormErrors(form_errors) {
        let error_div = document.createElement("div");
        for (let i = 0; i < form_errors.length; i++) {
            let p = document.createElement("p");
            p.textContent = form_errors[i];
            error_div.append(p);
        }
        return error_div;
    };

    // const buildForm = function buildForm(form_elm, form_data){
    /**
     * Builds elements for a form.
     * @param form_data
     * @returns {*[]}
     */
    const buildForm = function buildForm(form_data){
        // TODO: I think I do want to use field wrappers instead of defaults.
        console.debug('buildForm');
        let elms = [];
        // Form-level errors, fields, hidden_fields
        // buildFormErrors
        if (form_data.errors.length > 0) {
            console.debug('form-level errors exist');
            // form_elm.append(buildFormErrors(form_data.errors));
            elms.push(buildFormErrors(form_data.errors));
        }
        // buildFields
        for (let i = 0; i < form_data.fields.length; i++) {
            console.debug('buildForm -> buildFields');
            // buildWidgets(form_data.fields[i]);
            let field_data = form_data.fields[i];
            // form_elm.append(buildField(field_data));
            elms.push(buildField(field_data));
        }
        // buildHiddenFields
        for (let i = 0; i < form_data.hidden_fields.length; i++) {
            // TODO: create container for the hidden fields
            console.debug('buildForm -> buildHiddenFields');
            let field_data = form_data.hidden_fields[i];
            // form_elm.append(buildHidden(field_data));
            elms.push(buildHidden(field_data));
        }
        // TODO: CSRF?
        return elms;
    };

    const parseForm = function parseForm(elm, data) {
        // Formset or form
        if ("management_form" && "forms" in data) {
            // build a FormSet
            console.debug('detected formset');
            // buildForm(elm, data.management_form);
            let mgmt_form_elms = buildForm(data.management_form);
            for (let i = 0; i < mgmt_form_elms.length; i++) {
                elm.append(mgmt_form_elms[i]);
            }
            for (let form_idx = 0; form_idx < data.forms.length; form_idx++) {
                let form_wrapper = document.createElement("div");
                form_wrapper.setAttribute("class", "form-wrapper");
                let elms = buildForm(data.forms[form_idx]);
                for (let i = 0; i < elms.length; i++) {
                    form_wrapper.append(elms[i]);
                }
                elm.append(form_wrapper);
                // buildForm(elm, data.forms[i]);
            }
        } else if ("fields" && "errors" in data) {
            console.debug('detected form');
            let elms = buildForm(data);
            for (let i = 0; i < elms.length; i++) {
                elm.append(elms[i]);
            }
        }
        // Optional: add submit button
        let btn_submit = document.createElement("button");
        btn_submit.setAttribute("type", "submit");
        btn_submit.textContent = "Submit";
        elm.append(btn_submit);
    };

    return {
        // buildWidgets: buildWidgets,
        // buildForm: buildForm,
        parseForm: parseForm
    }
}());
