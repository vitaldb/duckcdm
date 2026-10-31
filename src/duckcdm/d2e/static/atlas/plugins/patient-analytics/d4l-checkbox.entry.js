import { r as registerInstance, h } from './index-001d5b4b.js';

const checkboxCss = ".checkbox.sc-d4l-checkbox{--size:23}input[type='checkbox'].sc-d4l-checkbox{position:absolute;height:1px;width:1px;overflow:hidden;clip:rect(1px, 1px, 1px, 1px);opacity:0}input[type='checkbox'].sc-d4l-checkbox+label.sc-d4l-checkbox{display:flex;position:relative;align-items:flex-start;color:var(--color-neutral);user-select:none;cursor:pointer}input[type='checkbox'].sc-d4l-checkbox+label.sc-d4l-checkbox::before{content:'';position:relative;display:inline-block;margin-right:var(--space-s);width:calc(var(--size) * 1px);height:calc(var(--size) * 1px);background:white;border:2px solid var(--color-primary);border-radius:5px;flex-shrink:0}input[type='checkbox'].sc-d4l-checkbox:checked+label.sc-d4l-checkbox::after{content:'';position:absolute;top:calc(var(--size) * 0.27 * 1px);left:calc(var(--size) * 0.22 * 1px);border-left:2px solid var(--color-primary);border-bottom:2px solid var(--color-primary);height:calc(var(--size) * 0.27 * 1px);width:calc(var(--size) * 0.63 * 1px);transform:rotate(-45deg)}input[type='checkbox'].sc-d4l-checkbox:focus+label.sc-d4l-checkbox::before{box-shadow:0 0 4px var(--color-primary-light)}input[type='checkbox'].sc-d4l-checkbox:disabled+label.sc-d4l-checkbox::before,input[type='checkbox'].sc-d4l-checkbox:disabled+label.sc-d4l-checkbox::after{border-color:var(--color-neutral-light)}input[type='checkbox'].sc-d4l-checkbox:disabled+label.sc-d4l-checkbox{color:var(--color-neutral-light)}input[type='checkbox'][aria-invalid='true'].sc-d4l-checkbox+label.sc-d4l-checkbox{color:var(--color-feedback-alarm)}input[type='checkbox'][aria-invalid='true'].sc-d4l-checkbox+label.sc-d4l-checkbox::before,input[type='checkbox'][aria-invalid='true'].sc-d4l-checkbox+label.sc-d4l-checkbox::after{border-color:var(--color-feedback-alarm)}.checkbox--reversed.sc-d4l-checkbox input[type='checkbox'].sc-d4l-checkbox+label.sc-d4l-checkbox{flex-direction:row-reverse;align-items:flex-start;justify-content:space-between}.checkbox--reversed.sc-d4l-checkbox input[type='checkbox'].sc-d4l-checkbox+label.sc-d4l-checkbox::before{margin-left:var(--space-s);margin-right:0}.checkbox--reversed.sc-d4l-checkbox input[type='checkbox'].sc-d4l-checkbox:checked+label.sc-d4l-checkbox::after{right:calc(var(--size) * 0.18 * 1px);left:unset}";

var __classPrivateFieldGet = (undefined && undefined.__classPrivateFieldGet) || function (receiver, state, kind, f) {
  if (kind === "a" && !f)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var __classPrivateFieldSet = (undefined && undefined.__classPrivateFieldSet) || function (receiver, state, value, kind, f) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return (kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value)), value;
};
var _Checkbox_checkboxElement, _Checkbox_inputElement;
const Checkbox = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    _Checkbox_checkboxElement.set(this, void 0);
    _Checkbox_inputElement.set(this, void 0);
    this.checkboxId = '';
    this.classes = '';
    this.name = '';
    this.checked = false;
    this.disabled = false;
    this.required = false;
    this.error = false;
    this.label = '';
    this.size = 23;
    this.value = '';
    this.focused = false;
    this.reversed = false;
    this.getClasses = () => {
      return `checkbox ${this.reversed ? 'checkbox--reversed' : ''} ${this.classes}`;
    };
  }
  componentDidLoad() {
    __classPrivateFieldGet(this, _Checkbox_checkboxElement, "f").style.setProperty('--size', this.size.toString());
    this.focused && window.requestAnimationFrame(() => __classPrivateFieldGet(this, _Checkbox_inputElement, "f").focus());
  }
  render() {
    const { checkboxId, getClasses, name, checked, disabled, label, error, required, handleChange, value, } = this;
    return (h("div", { class: getClasses(), ref: (el) => (__classPrivateFieldSet(this, _Checkbox_checkboxElement, el, "f")) }, h("input", { id: checkboxId, type: "checkbox", name: name, defaultChecked: checked, checked: checked, disabled: disabled, required: required, "aria-invalid": error.toString(), onChange: handleChange, value: value, ref: (el) => (__classPrivateFieldSet(this, _Checkbox_inputElement, el, "f")) }), h("label", { htmlFor: checkboxId }, label, h("slot", { name: "checkbox-label" }), required && h("slot", { name: "checkbox-required" }))));
  }
};
_Checkbox_checkboxElement = new WeakMap(), _Checkbox_inputElement = new WeakMap();
Checkbox.style = checkboxCss;

export { Checkbox as d4l_checkbox };
