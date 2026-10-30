import { r as registerInstance, h } from './index-001d5b4b.js';

const CookieBar = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.acceptText = 'Accept';
    this.rejectText = 'Reject';
    this.uppercaseButtons = false;
  }
  render() {
    const { classes, acceptText, rejectText, handleAccept, handleReject, uppercaseButtons, } = this;
    return (h("d4l-snack-bar", { classes: classes }, h("div", { slot: "snack-bar-content" }, h("slot", { name: "cookie-bar-text" })), h("div", { slot: "snack-bar-controls" }, h("d4l-button", { classes: `button--secondary button--small ${uppercaseButtons ? `button--uppercase` : ''}`, text: rejectText, type: "button", onClick: handleReject }), h("d4l-button", { classes: `button--primary button--small ${uppercaseButtons ? `button--uppercase` : ''}`, text: acceptText, type: "button", onClick: handleAccept }))));
  }
};

export { CookieBar as d4l_cookie_bar };
