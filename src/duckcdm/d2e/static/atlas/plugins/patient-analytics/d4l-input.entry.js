import { r as registerInstance, h } from './index-001d5b4b.js';

const inputCss = ".input.sc-d4l-input{display:block;position:relative;border:0;margin:15px 0 0 0;padding:0;width:100%;color:var(--color-primary)}.input__element.sc-d4l-input{font-family:inherit;font-size:16px;color:currentColor;width:100%;border:0;margin:0;display:block;padding:6px 0 8px;background:none;border-bottom:2px solid var(--color-neutral-lighter);transition:border-bottom-color 200ms cubic-bezier(0.4, 0, 0.2, 1) 0ms;outline:none;box-sizing:content-box;border-radius:0}.input__element.sc-d4l-input:disabled{color:var(--color-neutral-light);border-bottom-style:dotted}.input__element.sc-d4l-input:disabled~.input__label.sc-d4l-input{color:var(--color-neutral-light)}.input__label.sc-d4l-input{top:0;left:0;position:absolute;transform:translate(0, 5px) scale(1);transform-origin:top left;transition:color 200ms cubic-bezier(0, 0, 0.2, 1) 0ms,\n    transform 200ms cubic-bezier(0, 0, 0.2, 1) 0ms;pointer-events:none}.input__label--visuallyhidden.sc-d4l-input{border:0;clip:rect(0 0 0 0);height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute;width:1px}.input__element.sc-d4l-input::placeholder{color:var(--color-input-placeholder)}.input__element.sc-d4l-input:focus{border-bottom-color:var(--color-primary)}.input__element.sc-d4l-input:focus~.input__label.sc-d4l-input,.input__element.sc-d4l-input:not(:placeholder-shown)~.input__label.sc-d4l-input,.input__element.input__element--placeholder.sc-d4l-input~.input__label.sc-d4l-input{transform:translate(0, -15px) scale(0.85);color:var(--color-neutral)}.input__element.sc-d4l-input:-webkit-autofill~.input__label.sc-d4l-input{transform:translate(0, -15px) scale(0.85);color:var(--color-neutral)}.input__element.sc-d4l-input:invalid{box-shadow:none}.input__element--error.sc-d4l-input{border-bottom-color:var(--color-feedback-alarm)}.input__element.input__element--error.sc-d4l-input~.input__label.sc-d4l-input{color:var(--color-feedback-alarm)}.input__password-toggle.sc-d4l-input{position:absolute;right:0;top:-5px;padding:10px;background:none;border:0;cursor:pointer}.input--round.sc-d4l-input,.input--squared.sc-d4l-input{margin-top:0}.input--round.sc-d4l-input .input__element.sc-d4l-input{border:0 none;border-radius:1em;padding:8px 1em;box-sizing:border-box;box-shadow:var(--shadow-s);background-color:#fff;transition:box-shadow 0.2s ease-in-out}.input--squared.sc-d4l-input .input__element.sc-d4l-input{border:0 none;border-radius:var(--border-radius-s);padding:var(--space-s) calc(var(--space-m) * 2);box-sizing:border-box;box-shadow:var(--shadow-m);background-color:#fff;transition:box-shadow 0.2s ease-in-out;line-height:1.5}.input--round.sc-d4l-input .input__element.sc-d4l-input:focus,.input--squared.sc-d4l-input .input__element.sc-d4l-input:focus{box-shadow:var(--shadow-m)}.input--round.sc-d4l-input .input__label.sc-d4l-input,.input--squared.sc-d4l-input .input__label.sc-d4l-input{left:1em;right:1em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.input--round.sc-d4l-input .input__label.input__label.sc-d4l-input{transform:translate(0, 7px) scale(1);color:var(--color-neutral)}.input--squared.sc-d4l-input .input__label.input__label.sc-d4l-input{transform:translate(0, 17px) scale(1);color:var(--color-neutral);font-size:var(--font-size-desktop-m)}.input--round.sc-d4l-input .input__element.sc-d4l-input:not(:placeholder-shown)~.input__label.sc-d4l-input,.input--squared.sc-d4l-input .input__element.sc-d4l-input:not(:placeholder-shown)~.input__label.sc-d4l-input{display:none}.input--icons.sc-d4l-input .input__element.sc-d4l-input{padding-left:40px;padding-right:40px}.input--icons.sc-d4l-input .input__label.sc-d4l-input{left:40px}.input--small.sc-d4l-input .input__element.sc-d4l-input{width:4em}.input--medium.sc-d4l-input .input__element.sc-d4l-input{width:6em}.input--center.sc-d4l-input .input__element.sc-d4l-input{text-align:center}.input--center.sc-d4l-input .input__label.sc-d4l-input{left:50%;transform-origin:top center;transform:translate(-50%, 5px) scale(1);white-space:nowrap}.input--center.sc-d4l-input .input__element.sc-d4l-input:focus~.input__label.sc-d4l-input,.input--center.sc-d4l-input .input__element.sc-d4l-input:not(:placeholder-shown)~.input__label.sc-d4l-input,.input--center.sc-d4l-input .input__element.input__element--placeholder.sc-d4l-input~.input__label.sc-d4l-input{transform:translate(-50%, -15px) scale(0.85)}_.sc-d4l-input:-ms-lang(x),_.sc-d4l-input:-webkit-full-screen,.input__element.sc-d4l-input~.input__label.sc-d4l-input{top:-25px !important}";

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
var _Input_inputElement;
const Input = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    _Input_inputElement.set(this, void 0);
    this.inputId = null;
    this.classes = '';
    this.name = null;
    this.type = 'text';
    this.required = false;
    this.min = null;
    this.max = null;
    this.error = false;
    this.placeholder = ' ';
    this.label = 'Default text input';
    this.role = null;
    this.pattern = null;
    this.autocomplete = null;
    this.autocapitalize = null;
    this.ariaAutocomplete = null;
    this.ariaOwns = null;
    this.ariaExpanded = 'false';
    this.disabled = false;
    this.passwordToggle = false;
    this.focused = false;
    this.hiddenlabel = false;
    this.isPasswordVisible = false;
    this.togglePasswordVisibility = () => (this.isPasswordVisible = !this.isPasswordVisible);
    this.getClasses = () => {
      return `input__element ${this.placeholder.trim().length ? 'input__element--placeholder' : ''} ${this.error ? 'input__element--error' : ''}`;
    };
  }
  get inputType() {
    return this.type === 'password' && this.isPasswordVisible ? 'text' : this.type;
  }
  componentDidLoad() {
    this.focused && window.requestAnimationFrame(() => __classPrivateFieldGet(this, _Input_inputElement, "f").focus());
  }
  render() {
    const { inputId, classes, name, type, value, required, min, minlength, max, maxlength, step, error, placeholder, disabled, label, role, pattern, autocomplete, autocapitalize, ariaAutocomplete, ariaExpanded, ariaOwns, handleChange, handleInput, handleKeyUp, handleKeyDown, handleClick, handleFocus, handleBlur, isPasswordVisible, togglePasswordVisibility, passwordToggle, getClasses, inputType, inputmode, hiddenlabel, } = this;
    return (h("div", { class: `input ${classes}` }, h("input", { id: inputId, class: getClasses(), type: inputType, name: name, required: required, min: min, minlength: minlength, max: max, maxlength: maxlength, step: step, "aria-invalid": error.toString(), role: role, autocomplete: autocomplete, autocapitalize: autocapitalize, "aria-autocomplete": ariaAutocomplete, "aria-expanded": ariaAutocomplete === 'list' && ariaExpanded, "aria-owns": ariaOwns, placeholder: placeholder, pattern: pattern, disabled: disabled, onChange: handleChange, onInput: handleInput, onKeyUp: handleKeyUp, onKeyDown: handleKeyDown, onClick: handleClick, onFocus: handleFocus, onBlur: handleBlur, inputmode: inputmode, value: value, ref: (el) => (__classPrivateFieldSet(this, _Input_inputElement, el, "f")) }), h("label", { class: `${hiddenlabel ? 'input__label--visuallyhidden' : 'input__label'}`, htmlFor: inputId }, label, h("slot", { name: "input-required" })), type === 'password' && passwordToggle && (h("button", { class: `input__password-toggle ${isPasswordVisible && 'is-visible'}`, type: "button", "aria-label": "Toggle password visibility", tabindex: "0", onClick: () => togglePasswordVisibility() }, h("d4l-icon-show-hide", { classes: "icon--small", "is-visible": isPasswordVisible })))));
  }
};
_Input_inputElement = new WeakMap();
Input.style = inputCss;

export { Input as d4l_input };
