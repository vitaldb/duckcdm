import { r as registerInstance, h } from './index-001d5b4b.js';

const textareaCss = ".textarea.sc-d4l-textarea{display:block;position:relative;border:0;margin:15px 0 0 0;padding:0;width:100%;color:var(--color-primary)}.textarea__element.sc-d4l-textarea{font-family:inherit;font-size:16px;line-height:1.5;color:currentColor;width:100%;border:0;margin:0;display:block;padding:6px 0 8px;background:none;border-bottom:2px solid var(--color-neutral-lighter);transition:border-bottom-color 200ms cubic-bezier(0.4, 0, 0.2, 1) 0ms;outline:none;box-sizing:content-box;border-radius:0}.textarea__element.sc-d4l-textarea:disabled{color:var(--color-neutral-light);border-bottom-style:dotted}.textarea__element.sc-d4l-textarea:disabled~.textarea__label.sc-d4l-textarea{color:var(--color-neutral-light)}.textarea__label.sc-d4l-textarea{top:0;left:0;position:absolute;transform:translate(0, 5px) scale(1);transform-origin:top left;transition:color 200ms cubic-bezier(0, 0, 0.2, 1) 0ms,\n    transform 200ms cubic-bezier(0, 0, 0.2, 1) 0ms;pointer-events:none}.textarea__element.sc-d4l-textarea:focus{border-bottom-color:var(--color-primary)}.textarea__element.sc-d4l-textarea:focus~.textarea__label.sc-d4l-textarea,.textarea__element.sc-d4l-textarea:not(:placeholder-shown)~.textarea__label.sc-d4l-textarea,.textarea__element.textarea__element--placeholder.sc-d4l-textarea~.textarea__label.sc-d4l-textarea{transform:translate(0, -15px) scale(0.85);color:var(--color-neutral)}.textarea__element--error.sc-d4l-textarea{border-bottom-color:var(--color-feedback-alarm)}.textarea__element.textarea__element--error.sc-d4l-textarea~.textarea__label.sc-d4l-textarea{color:var(--color-feedback-alarm)}.textarea__character__counter.sc-d4l-textarea{display:flex;justify-content:flex-end;margin-top:calc(var(--space-xxs) / 2);color:var(--color-neutral-light)}.textarea__element.sc-d4l-textarea:focus~.textarea__character__counter.sc-d4l-textarea{color:var(--color-primary)}";

const Textarea = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.textareaId = null;
    this.classes = '';
    this.name = null;
    this.required = false;
    this.rows = null;
    this.maxlength = null;
    this.error = false;
    this.placeholder = ' ';
    this.label = null;
    this.autocapitalize = null;
    this.disabled = false;
    this.count = 0;
    this.getClasses = () => {
      return `textarea__element ${this.placeholder.trim().length ? 'textarea__element--placeholder' : ''} ${this.error ? 'textarea__element--error' : ''}`;
    };
    this.countCharacters = (event) => {
      this.count = event.target.value.length;
    };
  }
  render() {
    const { count, textareaId, classes, name, value, required, rows, maxlength, error, placeholder, disabled, label, autocapitalize, handleChange, handleInput, countCharacters, getClasses, } = this;
    return (h("div", { class: `textarea ${classes}` }, h("textarea", { id: textareaId, class: getClasses(), name: name, required: required, rows: rows, maxlength: maxlength, "aria-invalid": error.toString(), autocapitalize: autocapitalize, placeholder: placeholder, disabled: disabled, onChange: handleChange, onInput: handleInput, onKeyUp: countCharacters, value: value }, value), h("label", { class: "textarea__label", htmlFor: textareaId }, label, h("slot", { name: "textarea-required" })), maxlength && (h("div", { class: "textarea__character__counter" }, h("span", null, count), h("span", null, "/"), h("span", null, maxlength)))));
  }
};
Textarea.style = textareaCss;

export { Textarea as d4l_textarea };
