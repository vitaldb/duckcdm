import { r as registerInstance, h, H as Host } from './index-001d5b4b.js';

const accordionCss = ".sc-d4l-accordion-h{display:block;--color-header-background:var(--color-primary);--color-header-text:#fff;--color-header-background-open:var(--color-header-background);--color-header-text-open:var(--color-header-text);--color-panel-border:var(--color-header-background);--color-header-border:var(--color-header-background)}.accordion__header.sc-d4l-accordion{background-color:var(--color-header-background);color:var(--color-header-text);border-radius:var(--border-radius-s);border:1px solid var(--color-header-border)}.accordion__header--no-bottom-border-radius.sc-d4l-accordion{border-bottom-left-radius:0;border-bottom-right-radius:0;border-bottom:0;color:var(--color-header-text-open);background-color:var(--color-header-background-open)}.accordion__header.sc-d4l-accordion button.sc-d4l-accordion{border:0;background:transparent;display:flex;justify-content:space-between;align-items:center;width:100%;padding:1em 0.75em;color:inherit;cursor:pointer}.accordion__header--slim.sc-d4l-accordion button.sc-d4l-accordion{padding-top:0.5em;padding-bottom:0.5em}.accordion__panel.sc-d4l-accordion{border:1px solid var(--color-panel-border);border-radius:0 0 var(--border-radius-s) var(--border-radius-s);padding:0 0.5em}.accordion__panel[hidden='true'].sc-d4l-accordion{display:none}.accordion--no-panel-border.sc-d4l-accordion-h .accordion__panel.sc-d4l-accordion{border:0}.accordion--no-panel-padding.sc-d4l-accordion-h .accordion__panel.sc-d4l-accordion{padding:0}";

const Accordion = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.open = false;
    this.onExpandButtonClick = () => {
      var _a;
      this.open = !this.open;
      (_a = this.handleToggle) === null || _a === void 0 ? void 0 : _a.call(this, this.open);
    };
  }
  componentDidLoad() {
    if (this.headerBackgroundColor) {
      this.accordionElement.style.setProperty('--color-header-background', this.headerBackgroundColor);
    }
    if (this.headerBackgroundColorOpen) {
      this.accordionElement.style.setProperty('--color-header-background-open', this.headerBackgroundColorOpen);
    }
    if (this.headerTextColor) {
      this.accordionElement.style.setProperty('--color-header-text', this.headerTextColor);
    }
    if (this.headerTextColorOpen) {
      this.accordionElement.style.setProperty('--color-header-text-open', this.headerTextColorOpen);
    }
    if (this.panelBorderColor) {
      this.accordionElement.style.setProperty('--color-panel-border', this.panelBorderColor);
    }
    if (this.headerBorderColor) {
      this.accordionElement.style.setProperty('--color-header-border', this.headerBorderColor);
    }
  }
  render() {
    const { classes, open, onExpandButtonClick, buttonProps, slim } = this;
    return (h(Host, { class: `accordion ${classes}`, role: "region", open: open, ref: (el) => (this.accordionElement = el) }, h("div", { class: `accordion__header ${open ? 'accordion__header--no-bottom-border-radius' : ''} ${slim ? 'accordion__header--slim' : ''}` }, h("button", { "aria-expanded": open.toString(), onClick: () => onExpandButtonClick(), ...buttonProps }, h("slot", { name: "accordion-header" }), h("d4l-icon-arrow", { classes: `icon--medium icon--circle icon--bg-white icon--animated-transform ${open && 'icon--rotate-180'}`, focusable: "false" }))), h("div", { class: "accordion__panel", hidden: !open }, h("slot", { name: "accordion-panel" }))));
  }
};
Accordion.style = accordionCss;

export { Accordion as d4l_accordion };
