import { r as registerInstance, h } from './index-001d5b4b.js';

const cardStickyFooterCss = ".sticky-footer{position:sticky;bottom:0;z-index:2;background-color:#fff;box-shadow:0 -8px 8px 0 rgba(0, 0, 0, 0.08);width:100%}.sticky-footer.hide{display:none}";

const isInViewport = (element) => {
  const rect = element.getBoundingClientRect();
  return (rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth));
};
const CardStickyFooter = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.showStickyFooter = false;
  }
  handleScroll() {
    this.checkStatus();
  }
  componentDidRender() {
    // To ensure that the sticky footer is shown if needed
    this.checkStatus();
  }
  checkStatus() {
    this.showStickyFooter = this.companionId
      ? !isInViewport(document.getElementById(this.companionId))
      : false;
  }
  render() {
    return (h("div", { class: `sticky-footer c-button-stack u-padding--m ${this.showStickyFooter ? 'show' : 'hide'}` }, h("slot", null)));
  }
};
CardStickyFooter.style = cardStickyFooterCss;

export { CardStickyFooter as d4l_card_sticky_footer };
