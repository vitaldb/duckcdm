import { r as registerInstance, h } from './index-001d5b4b.js';

const bannerCss = "@keyframes bannerShrink{100%{height:0}}.banner.sc-d4l-banner{display:flex;flex-flow:row nowrap;align-items:center;background-color:var(--color-tertiary-light);color:var(--color-primary);font-size:16px;line-height:1.5;padding:0;margin:0;will-change:height}.banner--closing.sc-d4l-banner{overflow:hidden;pointer-events:none;animation:0.3s bannerShrink ease-in-out;animation-fill-mode:forwards}.banner__content.sc-d4l-banner,.banner__close.sc-d4l-banner{padding:1rem;margin:0;cursor:pointer;background:transparent;color:currentColor;font:inherit;font-weight:400;text-align:center;border:none;text-decoration:none}.banner__content.sc-d4l-banner{flex:1 1 auto}.banner__content--static.sc-d4l-banner{cursor:default}.banner__close.sc-d4l-banner{margin:0 0.5rem}.banner--slim.sc-d4l-banner .banner__content.sc-d4l-banner,.banner--slim.sc-d4l-banner .banner__close.sc-d4l-banner{padding:8px}.banner--slim.sc-d4l-banner .banner__close.sc-d4l-banner{margin:0 8px}.banner__invisible-slot.sc-d4l-banner{display:none}";

const Banner = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.noreferrer = false;
    this.show = true;
  }
  get isExternalLink() {
    var _a;
    return (((_a = this.link) === null || _a === void 0 ? void 0 : _a.includes('://')) && this.link.indexOf(document.location.origin) !== 0);
  }
  close(event) {
    const { height } = this.el.getBoundingClientRect();
    this.closingHeight = height;
    window.setTimeout(() => {
      this.handleClose && this.handleClose(event);
      this.show = false;
    }, 350);
  }
  render() {
    const { show, closingHeight, classes, text, closeButtonText, link, isExternalLink, noreferrer, handleClick, } = this;
    return ((show && (h("aside", { class: `banner ${classes} ${closingHeight ? 'banner--closing' : ''}`, ref: (el) => (this.el = el), style: { height: closingHeight ? `${closingHeight}px` : 'auto' } }, link ? (h("a", { href: link, target: isExternalLink ? '_blank' : '_self', rel: `noopener${noreferrer ? ' noreferrer' : ''}`, onClick: handleClick, class: "banner__content" }, h("slot", null, text))) : handleClick ? (h("button", { type: "button", onClick: handleClick, class: "banner__content" }, h("slot", null, text))) : (h("div", { class: "banner__content banner__content--static" }, h("slot", null, text))), h("button", { type: "button", onClick: (event) => this.close(event), class: "banner__close" }, h("span", { class: "u-visually-hidden" }, closeButtonText), h("d4l-icon-close", { classes: "icon--small" }))))) || (h("div", { class: "banner__invisible-slot" }, h("slot", null))));
  }
};
Banner.style = bannerCss;

export { Banner as d4l_banner };
