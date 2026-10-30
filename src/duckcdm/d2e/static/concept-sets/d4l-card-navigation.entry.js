import { r as registerInstance, h, H as Host } from './index-001d5b4b.js';

const cardNavigationCss = ".card-navigation{background-color:#fff;box-shadow:var(--shadow-s);position:sticky;top:calc(var(--header-height-mobile) + env(safe-area-inset-top, 0px));height:50px;width:100%;margin:0;display:flex;justify-content:center;border-top:1px solid var(--color-primary-extra-lightest);z-index:1;overflow:auto}.card-navigation nav{width:100%}@media screen and (min-width: 768px){.card-navigation{width:100%;margin:0;top:0}.card-navigation ul{justify-content:center}}.card-navigation ul{height:100%;display:flex;align-items:center;justify-content:center;margin:0}.card-navigation ul li{list-style:none;height:100%;display:flex;flex-direction:column;justify-content:space-between;padding:12px 10px 0}.card-navigation ul li button{border:none;margin:0;padding:0;width:auto;overflow:visible;color:inherit;font:inherit;line-height:normal;background:transparent;cursor:pointer}.card-navigation ul li::after{content:\" \";display:block;width:100%;height:var(--border-radius-xs);background-color:transparent}.card-navigation ul li.active::after{background-color:var(--color-primary);transition:all 0.4s ease-in-out}";

const CardNavigation = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.navigation = undefined;
    this.active = undefined;
    this.items = {};
    this.ariaLabel = 'card navigation';
  }
  handleScroll() {
    const scrollPosition = document.documentElement.scrollTop;
    const activeElement = Object.keys(this.items)
      .filter((id) => this.getPosition(id) <= scrollPosition)
      .at(-1);
    activeElement && this.setActive(activeElement);
  }
  setActive(id) {
    var _a;
    if (this.active === undefined || this.active !== id) {
      (_a = this.navigation.querySelector('li.active')) === null || _a === void 0 ? void 0 : _a.setAttribute('class', ' ');
      this.navigation.querySelector(`li#nav-${id}`).setAttribute('class', 'active');
      this.active = id;
    }
  }
  getPosition(id) {
    var _a;
    if (!this.items[id].position || this.items[id].position === 0) {
      this.items[id].position = ((_a = document.getElementById(id)) === null || _a === void 0 ? void 0 : _a.offsetTop) || 0;
    }
    return -1 * this.navigationHeight + this.items[id].position + 2;
  }
  componentDidRender() {
    this.navigationHeight = this.navigation ? this.navigation.clientHeight : 0;
  }
  render() {
    if (Object.keys(this.items).length === 0) {
      return null;
    }
    return (h(Host, { class: "card-navigation" }, h("nav", { ref: (el) => (this.navigation = el), "aria-label": this.ariaLabel }, h("ul", null, Object.keys(this.items).map((id, index) => (h("li", { id: `nav-${id}`, class: `${index === 0 ? 'active' : ''}` }, h("button", { onClick: () => {
        window.requestAnimationFrame(() => document.documentElement.scroll({
          top: this.getPosition(id),
          behavior: 'smooth',
        }));
        this.setActive(id);
      } }, this.items[id].title()))))))));
  }
};
CardNavigation.style = cardNavigationCss;

export { CardNavigation as d4l_card_navigation };
