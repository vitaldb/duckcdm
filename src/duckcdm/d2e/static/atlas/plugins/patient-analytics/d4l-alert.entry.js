import { r as registerInstance, h } from './index-001d5b4b.js';

const alertCss = ".alert.sc-d4l-alert{border-left:0.125em solid transparent;color:var(--color-primary);margin:1.25em auto;padding:1em;position:relative;background-color:transparent}.alert__background.sc-d4l-alert{position:absolute;top:0;left:0;right:0;bottom:0;opacity:0.1;z-index:0}.alert__content.sc-d4l-alert{position:relative;z-index:1}.alert--error.sc-d4l-alert{border-color:var(--color-feedback-alarm)}.alert--error.sc-d4l-alert .alert__background.sc-d4l-alert{background-color:var(--color-feedback-alarm)}.alert--success.sc-d4l-alert{border-color:var(--color-primary)}.alert--success.sc-d4l-alert .alert__background.sc-d4l-alert{background-color:var(--color-primary)}.alert--notification.sc-d4l-alert{border-color:var(--color-neutral-light)}.alert--notification.sc-d4l-alert .alert__background.sc-d4l-alert{background-color:var(--color-neutral-light)}";

const TYPE_CLASSES = {
  error: 'alert--error',
  success: 'alert--success',
  notification: 'alert--notification',
};
const Alert = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.type = null; // success, error, notification
    this.typeClass = this.type ? TYPE_CLASSES[this.type] : '';
    this.getClasses = () => `alert ${this.classes} ${this.typeClass}`;
  }
  render() {
    const { getClasses } = this;
    return (h("div", { class: getClasses(), role: "alert" }, h("div", { class: "alert__content" }, h("slot", null)), h("div", { class: "alert__background" })));
  }
};
Alert.style = alertCss;

export { Alert as d4l_alert };
