import { r as registerInstance, h } from './index-001d5b4b.js';

const selectCss = ".select.sc-d4l-select{display:block;position:relative;margin:15px 0 0 0;width:100%;color:var(--color-primary);font-size:16px}.select__element.sc-d4l-select{font-family:inherit;font-size:inherit;cursor:pointer;width:100%;outline:none;border-radius:0;border:0;border-bottom:2px solid var(--color-neutral-lighter);color:currentColor;padding:6px 24px 8px 0;background:none;-moz-appearance:none;-webkit-appearance:none}.select__element.sc-d4l-select:focus{border-bottom-color:var(--color-primary)}.select__element.sc-d4l-select:disabled{cursor:not-allowed;color:var(--color-neutral-light);border-bottom-style:dotted}.select__label.sc-d4l-select{position:absolute;top:-15px;left:0;font-size:85%;color:var(--color-neutral)}.select__icon.sc-d4l-select{position:absolute;right:0;top:-2px;padding:10px;pointer-events:none}";

const Select = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.selectId = null;
    this.classes = '';
    this.label = null;
    this.options = [];
    this.selectedValue = '';
    this.disabled = false;
    this.required = false;
  }
  render() {
    const { selectId, classes, label, options, selectedValue, disabled, required, handleChange, } = this;
    return (h("div", { class: `select ${classes}` }, h("select", { id: selectId, class: "select__element", disabled: disabled, required: required, onChange: handleChange }, h("slot", { name: "select-option-default" }), !!options.length && options.map((option) => (h("option", { value: option.value, selected: selectedValue == option.value }, option.text))), h("slot", { name: "select-option" })), h("span", { class: "select__icon" }, h("d4l-icon-arrow", { classes: "icon--extra-small" })), h("label", { class: "select__label", htmlFor: selectId }, label, h("slot", { name: "select-required" }))));
  }
};
Select.style = selectCss;

export { Select as d4l_select };
