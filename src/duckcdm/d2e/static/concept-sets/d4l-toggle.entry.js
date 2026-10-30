import { r as registerInstance, h } from './index-001d5b4b.js';

const toggleCss = ".toggle.sc-d4l-toggle{display:inline-block;line-height:0}.toggle__input.sc-d4l-toggle{display:block;position:relative;width:51px;height:32px;margin:0;-webkit-appearance:none;outline:none;border:2px solid var(--color-neutral-lightest);border-radius:50px;background-color:#fff;cursor:pointer;box-shadow:inset -19px 0 0 0 var(--color-neutral-lightest);transition:box-shadow 0.2s ease-in-out, border-color 0.2s ease-in-out}.toggle__input.sc-d4l-toggle:focus::before{content:'';position:absolute;top:-2px;bottom:-2px;left:-2px;right:-2px;border-radius:50px;box-shadow:0px 0px 5px 2px var(--color-primary-lightest);z-index:-1}.toggle__input.sc-d4l-toggle::after{content:'';position:absolute;top:0px;left:0px;width:28px;height:28px;background:transparent;border-radius:50%;box-shadow:2px 4px 6px rgba(0, 0, 0, 0.05);transition:left 0.2s ease-in-out, box-shadow 0.2s ease-in-out}.toggle__input.sc-d4l-toggle:checked{border-color:var(--color-primary-light);box-shadow:inset 19px 0 0 0 var(--color-primary-light)}.toggle__input.sc-d4l-toggle:checked:focus::before{content:'';position:absolute;top:-2px;bottom:-2px;left:-2px;right:-2px;border-radius:50px;box-shadow:0px 0px 5px 2px var(--color-primary-lightest);z-index:-1}.toggle__input.sc-d4l-toggle:checked::after{left:19px;box-shadow:-2px 4px 3px rgba(0, 0, 0, 0.05)}";

const Toggle = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.inputId = 'toggle-input';
    this.hoverText = '';
    this.checked = false; // initial state passed from the outside
  }
  componentWillLoad() {
    this.active = this.checked; // set state to initial one from prop
  }
  render() {
    return (h("label", { class: { toggle: true, 'toggle--active': this.active } }, h("input", { id: this.inputId, title: this.hoverText, type: "checkbox", class: "toggle__input", checked: this.checked, onChange: (event) => {
        this.active = event.target.checked;
        this.handleChange(event);
      }, role: "checkbox", "aria-checked": this.checked, "aria-label": this.label })));
  }
};
Toggle.style = toggleCss;

export { Toggle as d4l_toggle };
