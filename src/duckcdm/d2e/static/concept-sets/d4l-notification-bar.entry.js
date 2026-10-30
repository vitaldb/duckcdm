import { r as registerInstance, h } from './index-001d5b4b.js';

const notificationBarCss = ".notification-bar.sc-d4l-notification-bar{display:flex;border-radius:var(--border-radius-medium, var(--border-radius-s));background-color:var(--color-primary-extra-lightest);color:var(--color-primary);font-size:1rem;padding:1.25em 1.5em}.notification-bar--slim.sc-d4l-notification-bar{padding:0.875em}.notification-bar__icon.sc-d4l-notification-bar{flex:none;margin-right:1em}.notification-bar__headline.sc-d4l-notification-bar{font-size:1em;font-weight:500}.notification-bar__text.sc-d4l-notification-bar{flex:0 1 auto;overflow:hidden;font-size:0.875em}.notification-bar__link.sc-d4l-notification-bar{text-decoration:none;font-weight:500;color:inherit}.notification-bar__link.sc-d4l-notification-bar:hover{text-decoration:underline}.notification-bar--no-background-color.sc-d4l-notification-bar{background-color:initial}.notification-bar--bgcolor-red.sc-d4l-notification-bar{background-color:var(--color-feedback-alarm)}.notification-bar--color-neutral.sc-d4l-notification-bar{color:var(--color-neutral)}.notification-bar--color-white.sc-d4l-notification-bar{color:#fff}.notification-bar--centered.sc-d4l-notification-bar{justify-content:center}.notification-bar--centered.sc-d4l-notification-bar .notification-bar__icon.sc-d4l-notification-bar{margin-right:0.5em}.notification-bar--centered.sc-d4l-notification-bar .notification-bar__headline.sc-d4l-notification-bar{display:flex;justify-content:center;align-items:center}@media (min-width: 768px){.notification-bar.sc-d4l-notification-bar{align-items:center}}";

const NotificationBar = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.text = '';
    this.headline = '';
    this.textLink = '';
    this.link = '';
    this.centered = false;
    this.icon = 'info';
    this.hasLink = false;
    this.getIconInfo = () => {
      const { icon } = this;
      return (h("div", { class: "notification-bar__icon" }, h("d4l-icon", { iconName: icon, iconClasses: "icon--small icon--current-color" })));
    };
  }
  componentWillLoad() {
    this.hasLink = !!this.text.length && !!this.textLink.length;
  }
  render() {
    const { classes, text, headline, textLink, link, hasLink, centered } = this;
    return (h("aside", { class: `notification-bar ${classes}` }, !centered && this.getIconInfo(), h("div", { class: "notification-bar__content" }, !!headline.length && (h("div", { class: "notification-bar__headline" }, centered && this.getIconInfo(), headline)), h("div", { class: "notification-bar__text" }, text, ' ', hasLink && (h("a", { class: "notification-bar__link", href: link, rel: "noopener noreferrer" }, textLink))), h("slot", { name: "bar-content" }))));
  }
};
NotificationBar.style = notificationBarCss;

export { NotificationBar as d4l_notification_bar };
