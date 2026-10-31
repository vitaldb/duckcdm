import { r as registerInstance, h, g as getElement } from './index-001d5b4b.js';
import { h as href } from './index-13b9ea17.js';

const appHeaderCss = ".app-header{display:flex;align-items:center;padding:20px var(--space-s);margin:0 auto;width:var(--widescreen);max-width:100%;color:var(--color-primary)}.app-header__navigation{display:flex;flex-flow:row nowrap;align-items:center;margin-left:auto}.app-header__logo_link{display:flex}img.app-header__custom-logo{height:var(--space-l)}.app-header__navigation svg{width:var(--space-m);height:var(--space-m)}.app-header__navigation-link{color:currentColor;height:var(--space-m);margin:0;box-sizing:content-box;text-decoration:none;display:grid;grid-template-columns:1fr;grid-template-rows:24px 15px 3px;gap:0px;align-items:center;justify-items:center;height:100%;padding:1px var(--space-s)}.app-header__navigation-divider{width:1px;height:var(--space-m);background:var(--color-primary)}.app-header__navigation-link:after{content:'';height:2px;width:110%;background-color:transparent;transition:0.3s background-color ease-in-out;grid-column:1/-1}.app-header__navigation-link--active:after{background-color:currentColor}.app-header__navigation-link__title{font-size:var(--font-size-desktop-xs);color:var(--color-primary)}@media screen and (min-width: 768px){.app-header__navigation-link{grid-template-columns:24px 1fr;grid-template-rows:24px 2px;gap:2px 0px;align-items:center;padding:8px var(--space-s)}.app-header__navigation-link__title{margin-left:var(--space-xs)}}.app-header__navigation-link--no-margin{padding:0;display:flex}.app-header d4l-navigation-menu{margin-right:var(--space-s)}";

const Fragment = (_props, children) => children;
const AppHeader = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.logoUrl = '';
    this.logoUrlText = '';
    this.logoUrlTitle = 'Home link';
    this.isBetaLogo = false;
    this.isCompactLogo = false;
    this.hasLogo = true;
    this.menuNavigationNotification = false;
    this.menuFooterLinks = [];
  }
  componentWillLoad() {
    this.hasTitleSlot = !!this.hostElement.querySelector('[slot="app-header-title"]');
  }
  get logo() {
    const { customLogo, logoUrlText, isCompactLogo, isBetaLogo } = this;
    return customLogo ? (h("img", { class: "app-header__custom-logo", src: customLogo, "data-test": "logo", alt: logoUrlText })) : (h("d4l-company-logo", { compact: isCompactLogo, beta: isBetaLogo, "data-test": "logo" }));
  }
  renderLogo() {
    const { logoUrl, logoUrlText, logoUrlTitle, router, logo } = this;
    if (!!logoUrl && !!logoUrlText && !!router) {
      return (h("a", { class: "app-header__logo_link", title: logoUrlTitle, ...href(logoUrl, router) }, logo, h("span", { class: "u-visually-hidden" }, logoUrlText)));
    }
    return logo;
  }
  renderTopNavigation() {
    const { topNavigationItems, handleNavigationItemAnalytics, router } = this;
    return topNavigationItems
      .filter(({ condition }) => condition)
      .map((item, index) => (h(Fragment, null, index > 0 && h("div", { class: "app-header__navigation-divider" }), item.subItems && item.subItems.length ? (this.renderTopNavigationSubMenu(item)) : (h("a", { title: item.title, class: {
        'app-header__navigation-link': true,
        'app-header__navigation-link--active': router.activePath.startsWith(item.route),
      }, "data-test": item.dataTest, "data-test-context": item.dataTestContext, onClick: () => {
        item.trackingEvent && handleNavigationItemAnalytics
          ? handleNavigationItemAnalytics(item.trackingEvent)
          : null;
      }, ...href(item.route, router) }, h("d4l-icon", { iconName: item.icon }), h("div", { class: "app-header__navigation-link__title" }, item.title))))));
  }
  renderTopNavigationSubMenu(item) {
    const { handleNavigationItemAnalytics, router } = this;
    return (h("div", { class: "app-header__navigation-link app-header__navigation-link--no-margin", onClick: () => {
        item.trackingEvent && handleNavigationItemAnalytics
          ? handleNavigationItemAnalytics(item.trackingEvent)
          : null;
      } }, h("d4l-navigation-menu", { classes: "is-sub-menu", direction: 'left', menuButtonShow: true, menuButtonIcon: item.icon, menuButtonLabel: item.title, menuButtonLabelShow: item.showTitle, menuCardTitle: item.subMenuTitle || item.title, navigationItems: item.subItems, handleNavigationItemAnalytics: handleNavigationItemAnalytics, router: router })));
  }
  render() {
    const { classes, topNavigationItems, menuNavigationItems, menuButtonLabel, menuCardTitle, menuFooterLinks, menuFooterLinksIndex, supportedLanguages, selectedLanguage, hasTitleSlot, hasLogo, handleNavigationItemAnalytics, handleMenuAnalytics, router, } = this;
    return (h("header", { class: `app-header ${classes}` }, menuNavigationItems && (h("d4l-navigation-menu", { classes: "navigation-menu__embedded", menuButtonLabel: menuButtonLabel, menuCardTitle: menuCardTitle, navigationItems: menuNavigationItems, notification: this.menuNavigationNotification, supportedLanguages: supportedLanguages, selectedLanguage: selectedLanguage, menuFooterLinks: menuFooterLinks, menuFooterLinksIndex: menuFooterLinksIndex, handleNavigationItemAnalytics: handleNavigationItemAnalytics, handleMenuAnalytics: handleMenuAnalytics, router: router })), h("div", { class: "app-header__title" }, !hasTitleSlot && hasLogo && this.renderLogo(), h("slot", { name: "app-header-title" })), h("nav", { class: "app-header__navigation" }, topNavigationItems && this.renderTopNavigation(), !topNavigationItems && !menuNavigationItems && supportedLanguages && (h("d4l-language-switcher", { "data-test": "languageSwitcher", languages: supportedLanguages, activeLanguage: selectedLanguage })))));
  }
  get hostElement() { return getElement(this); }
};
AppHeader.style = appHeaderCss;

export { AppHeader as d4l_app_header };
