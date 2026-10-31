import { r as registerInstance, h } from './index-001d5b4b.js';

const radioCss = ".radio.sc-d4l-radio{--size:23}.radio.sc-d4l-radio{position:relative}input[type='radio'].sc-d4l-radio{position:absolute;height:1px;width:1px;overflow:hidden;clip:rect(1px, 1px, 1px, 1px);opacity:0;left:calc(((var(--size) / 3) - 1) * 1px);top:calc(var(--size) * 1px)}input[type='radio'].sc-d4l-radio+label.sc-d4l-radio{display:flex;position:relative;align-items:flex-start;color:var(--color-neutral);user-select:none}input[type='radio'].sc-d4l-radio+label.sc-d4l-radio::before{content:'';position:relative;display:inline-block;margin-right:1em;width:calc(var(--size) * 1px);height:calc(var(--size) * 1px);background:white;border:2px solid var(--color-primary);border-radius:100%;flex-shrink:0}input[type='radio'].sc-d4l-radio:checked+label.sc-d4l-radio::after{content:'';position:absolute;top:5px;left:5px;height:calc((var(--size) * 1px) - 10px);width:calc((var(--size) * 1px) - 10px);border-radius:100%;background-color:var(--color-primary)}input[type='radio'].sc-d4l-radio:focus+label.sc-d4l-radio::before{box-shadow:0 0 4px var(--color-primary-light)}input[type='radio'].sc-d4l-radio:disabled+label.sc-d4l-radio::before,input[type='radio'].sc-d4l-radio:disabled+label.sc-d4l-radio::after{border-color:var(--color-neutral-light)}input[type='radio'].sc-d4l-radio:disabled+label.sc-d4l-radio{color:var(--color-neutral-light)}input[type='radio'][aria-invalid='true'].sc-d4l-radio+label.sc-d4l-radio{color:var(--color-feedback-alarm)}input[type='radio'][aria-invalid='true'].sc-d4l-radio+label.sc-d4l-radio::before,input[type='radio'][aria-invalid='true'].sc-d4l-radio+label.sc-d4l-radio::after{border-color:var(--color-feedback-alarm)}";

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
var _Radio_radioElement, _Radio_inputElement;
const Radio = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    _Radio_radioElement.set(this, void 0);
    _Radio_inputElement.set(this, void 0);
    this.radioId = '';
    this.classes = '';
    this.name = '';
    this.checked = false;
    this.disabled = false;
    this.required = false;
    this.requiredText = '';
    this.error = false;
    this.label = '';
    this.size = 23;
    this.value = '';
    this.focused = false;
  }
  componentDidLoad() {
    __classPrivateFieldGet(this, _Radio_radioElement, "f").style.setProperty('--size', this.size.toString());
    this.focused && window.requestAnimationFrame(() => __classPrivateFieldGet(this, _Radio_inputElement, "f").focus());
  }
  render() {
    const { radioId, classes, name, checked, disabled, label, error, required, requiredText, handleChange, value, } = this;
    return (h("div", { class: `radio ${classes}`, ref: (el) => (__classPrivateFieldSet(this, _Radio_radioElement, el, "f")) }, h("input", { id: radioId, type: "radio", name: name, checked: checked, disabled: disabled, required: required, "aria-invalid": error.toString(), onChange: handleChange, value: value, ref: (el) => (__classPrivateFieldSet(this, _Radio_inputElement, el, "f")) }), h("label", { htmlFor: radioId }, label, h("slot", { name: "radio-label" }), required && requiredText)));
  }
};
_Radio_radioElement = new WeakMap(), _Radio_inputElement = new WeakMap();
Radio.style = radioCss;

export { Radio as d4l_radio };
