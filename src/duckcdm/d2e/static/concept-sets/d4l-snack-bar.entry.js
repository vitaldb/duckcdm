import { r as registerInstance, h } from './index-001d5b4b.js';

const snackBarCss = ".snack-bar{display:flex;flex-direction:column;padding:1em;background-color:#fff;color:var(--color-primary)}.snack-bar__content{display:flex;align-items:flex-start}.snack-bar__controls:not(:empty){margin-top:0.5em;margin-left:auto;padding-left:1em;flex-shrink:0}.snack-bar--error{background-color:var(--color-feedback-alarm);color:#fff}.snack-bar--success{background-color:var(--color-primary);color:#fff}.snack-bar--error .icon,.snack-bar--success .icon{fill:#fff}.snack-bar--error d4l-button .button--text,.snack-bar--success d4l-button .button--text,.snack-bar--error d4l-button .button--text:hover,.snack-bar--success d4l-button .button--text:hover{color:#fff}.snack-bar--notification{background-color:var(--color-primary-extra-lightest);color:var(--color-primary);font-weight:400}.snack-bar--confirm{background-color:var(--color-neutral-lightest);color:var(--color-primary);font-weight:400}.snack-bar__controls d4l-button+d4l-button{margin-left:0.5em}@media screen and (min-width: 768px){.snack-bar{flex-direction:row;align-items:center}.snack-bar__content{align-items:center}.snack-bar__controls:not(:empty){margin-top:0}}";

const TYPE_CLASSES = {
  error: 'snack-bar--error',
  success: 'snack-bar--success',
  notification: 'snack-bar--notification',
  confirm: 'snack-bar--confirm',
};
const SnackBar = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.type = null; // success, error, notification
    this.getClasses = () => `snack-bar ${this.classes} ${this.type ? TYPE_CLASSES[this.type] : ''}`;
  }
  render() {
    const { getClasses } = this;
    return (h("div", { class: getClasses() }, h("div", { class: "snack-bar__content" }, h("slot", { name: "snack-bar-icon" }), h("slot", { name: "snack-bar-content" })), h("div", { class: "snack-bar__controls" }, h("slot", { name: "snack-bar-controls" }))));
  }
};
SnackBar.style = snackBarCss;

export { SnackBar as d4l_snack_bar };
