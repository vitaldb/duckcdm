import { r as registerInstance, h } from './index-001d5b4b.js';
import { h as href } from './index-13b9ea17.js';
import { K as KEY_EVENTS } from './constants-c55fb626.js';

const companyLogoCss = ":host{display:block}.company-logo{display:block;width:54px;height:24px}.company-logo--compact{height:1em;width:auto}";

const CompanyLogo = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.compact = false;
    this.beta = false;
  }
  get svgCompact() {
    return (h("svg", { class: "company-logo company-logo--compact", xmlns: "http://www.w3.org/2000/svg", viewBox: "0 0 210 92" }, h("path", { fill: "#000E7E", d: "M96.6 51.23l33.6-50.18H96.6L63 51.23h33.6zm17.85 9.4c-8.7 0-15.75 7.03-15.75 15.69S105.75 92 114.45 92s15.75-7.02 15.75-15.68-7.05-15.68-15.75-15.68zm66.15 3.14V1.05h-28.35v89.9H210V63.77h-29.4zM0 0c25.52 0 46.2 20.6 46.2 46S25.51 92 0 92V0z" })));
  }
  get svgNormal() {
    return (h("svg", { width: "210", height: "92", viewBox: "0 0 210 92", class: "company-logo", xmlns: "http://www.w3.org/2000/svg" }, h("defs", null, h("path", { id: "a", d: "M0 0h210v92H0z" })), h("g", { fill: "none", "fill-rule": "evenodd" }, h("mask", { id: "b", fill: "#fff" }, h("use", { xlinkHref: "#a" })), h("path", { d: "M96.6 51.228l33.6-50.181H96.6L63 51.227h33.6zm17.85 9.408c-8.698 0-15.75 7.021-15.75 15.682 0 8.66 7.052 15.682 15.75 15.682s15.75-7.021 15.75-15.682c0-8.66-7.052-15.682-15.75-15.682zm66.15 3.138V1.047h-28.35v89.908H210V63.774h-29.4zM0 0c25.515 0 46.2 20.595 46.2 46S25.515 92 0 92V0z", fill: "#020D7D", "fill-rule": "nonzero", mask: "url(#b)" }))));
  }
  get svgBeta() {
    return (h("svg", { width: "78", height: "24", xmlns: "http://www.w3.org/2000/svg", "fill-rule": "evenodd", "clip-rule": "evenodd", "stroke-linejoin": "round", "stroke-miterlimit": "2" }, h("g", { fill: "#000e7e" }, h("path", { d: "M24.353 13.612L33.176.716h-8.823l-8.824 12.896h8.824zm4.765 2.15c-2.242 0-4.06 1.844-4.06 4.119 0 2.275 1.818 4.119 4.06 4.119 2.241 0 4.058-1.844 4.058-4.12 0-2.274-1.817-4.119-4.058-4.119v.001zm16.63 1.199V.716H38.47V24h14.823v-7.04h-7.546l.001.001zM0 0c6.238 0 11.294 5.373 11.294 12S6.238 24 0 24V0zM57.174 4.35c.462.078.824.278 1.087.6.263.32.394.728.394 1.223 0 .353-.08.685-.24.996-.16.31-.426.567-.799.768-.373.201-.861.302-1.465.302h-2.857V.716h2.633c.902 0 1.547.198 1.934.594.387.395.581.865.581 1.409 0 .374-.108.71-.325 1.006-.217.297-.531.505-.943.625zm-2.867-2.786V3.98h1.62c1.009 0 1.513-.396 1.513-1.187 0-.353-.112-.646-.336-.88-.223-.232-.616-.349-1.177-.349h-1.62zm1.79 5.827c.547 0 .944-.123 1.189-.37.245-.248.367-.562.367-.944 0-.374-.119-.676-.357-.905-.238-.23-.602-.345-1.092-.345h-1.897v2.564h1.79zm8.975 0v.848h-4.765V.716h4.69v.848H61.32v2.394h3.496v.848H61.32v2.585h3.752zm6.672-5.827h-2.377v6.675h-1.013V1.564h-2.377V.716h5.767v.848zm4.433 4.503h-3.09l-.779 2.172h-1.044L74.131.716h1.002L78 8.24h-1.045l-.778-2.172v-.001zm-.298-.848l-1.055-2.935a6.43 6.43 0 0 1-.181-.572h-.022a6.423 6.423 0 0 1-.18.572L73.384 5.22h2.494l.001-.001z" }))));
  }
  render() {
    return this.compact
      ? this.svgCompact
      : this.beta
        ? this.svgBeta
        : this.svgNormal;
  }
};
CompanyLogo.style = companyLogoCss;

const navigationMenuCss = ".navigation-menu{display:block;position:relative;z-index:var(--z-index-navigation-menu)}button[aria-haspopup]{padding:14px 10px;cursor:pointer}.is-sub-menu{z-index:var(--z-index-navigation-sub-menu)}.is-sub-menu button[aria-haspopup]{padding:0}.navigation-menu__burger{display:block;width:24px;height:2px;margin-bottom:5px;border-radius:2px;background-color:var(--color-primary);transition:transform 0.25s cubic-bezier(1, 0, 0, 1),\n    opacity 0.25s cubic-bezier(1, 0, 0, 1)}.navigation-menu__burger--no-margin{margin:0}button[aria-expanded='true'] span.navigation-menu__burger:nth-of-type(1){transform:rotate(45deg) translate(5px, 4px)}button[aria-expanded='true'] span.navigation-menu__burger:nth-of-type(2){opacity:0}button[aria-expanded='true'] span.navigation-menu__burger:nth-of-type(3){transform:rotate(-45deg) translate(6px, -5px)}.navigation-menu__icon-button{color:currentColor;height:var(--space-m);margin:0;box-sizing:content-box;text-decoration:none;display:grid;grid-template-columns:1fr;grid-template-rows:24px 15px 3px;gap:0px;align-items:center;justify-items:center;height:100%;padding:1px var(--space-s)}.navigation-menu__icon-button.navigation-menu__icon-button--no-label{grid-template-rows:30px}.navigation-menu__icon-button .navigation-menu__icon-button__label{font-size:var(--font-size-desktop-xs);color:var(--color-primary)}.navigation-menu__close-button{display:inline-block;border:none;margin:0;padding:0;background:transparent}button .navigation-menu__icon-button:after{content:'';height:2px;width:110%;background-color:transparent;transition:0.3s background-color ease-in-out;grid-column:1/-1}button[aria-expanded='true'] .navigation-menu__icon-button:not(.navigation-menu__icon-button--no-label):after{background-color:var(--color-primary)}.navigation-menu button{position:relative}.navigation-menu__dot{position:absolute;right:9px;top:9px;width:10px;height:10px;border-radius:100%;background-color:var(--color-secondary)}button[aria-expanded='true'] .navigation-menu__dot{display:none}ul[role='menu'] li{border-top:1px solid var(--color-primary-extra-lightest)}ul[role='menu'] li:first-of-type,ul[role='menu'] li.navigation-menu__sub-item{border-top:1px solid transparent}ul[role='menu'] li:last-of-type{border-bottom:1px solid var(--color-primary-extra-lightest)}ul[role='menu'] li>button,ul[role='menu'] li>a{display:flex;align-items:center;text-decoration:none;padding:var(--space-s);color:var(--color-primary);width:100%;cursor:pointer}ul[role='menu'] li.navigation-menu__sub-item>a{padding-top:var(--space-xxs);padding-bottom:var(--space-xxs)}ul[role='menu'] li>button:focus,ul[role='menu'] li>button:hover,ul[role='menu'] li>a:focus,ul[role='menu'] li>a:hover{background-color:var(--color-neutral-extra-lightest)}.navigation-menu__sub-item__icon{min-width:36px}.navigation-menu__link-container{margin-left:var(--space-s);margin-right:var(--space-xs)}.navigation-menu__link-container--no-left-margin{margin-left:0}.navigation-menu__link-container--no-icon{margin-left:var(--space-s);padding-left:36px}.navigation-menu__link-container>p{font-size:0.875rem;font-weight:100;margin:0}.navigation-menu__link-text{font-weight:500;font-size:0.875rem;line-height:1.5;font-family:var(--font-family-secondary)}.navigation-menu__header{border-bottom:1px solid var(--color-primary-lightest);display:flex;flex-direction:row;justify-content:space-between;align-items:center}.navigation-menu__header>span{display:block;font-weight:500;font-size:var(--font-size-mobile-xl);color:var(--color-primary)}.navigation-menu__card{width:288px;margin:var(--space-l) auto 0;position:absolute;display:none}.navigation-menu__card--right-aligned{left:0}.navigation-menu__card--left-aligned{right:0}.navigation-menu__header{padding:var(--space-m)}.navigation-menu__content--padded{padding-bottom:var(--space-xl)}ul.navigation-menu__footer{display:flex;flex-direction:row;width:100%;margin:0 auto;justify-content:center;flex-wrap:wrap}ul.navigation-menu__footer li{display:flex;flex-basis:auto;justify-content:center;white-space:nowrap;align-items:center}ul.navigation-menu__footer li .navigation-menu__footer__link{cursor:pointer;color:var(--color-neutral);font-size:var(--font-size-desktop-xs);text-decoration:none}ul.navigation-menu__footer li:not(:first-of-type) .navigation-menu__footer__link::before{content:'';width:2px;height:2px;border-radius:50%;background:var(--color-neutral);display:inline-block;margin:3px 5px}ul.navigation-menu__footer li .navigation-menu__footer__link:hover,ul.navigation-menu__footer li .navigation-menu__footer__link:focus{text-decoration:underline}button[aria-expanded='true']~.navigation-menu__card{display:block}@media screen and (max-width: 767px) and (orientation: portrait), (max-width: 949px) and (orientation: landscape){.navigation-menu__header{padding-right:var(--space-s)}.navigation-menu__header d4l-language-switcher{display:none}.navigation-menu__embedded .card{display:block;width:100vw;height:100vh;margin:0;top:0;left:0;overflow:auto;position:fixed}.navigation-menu__embedded .card .card__header{position:sticky;top:0;background-color:var(--card-default-background-color)}button[aria-expanded='true']~.navigation-menu__card .card{border-radius:0;padding-top:env(safe-area-inset-top, 0px)}}@media screen and (min-width: 768px) and (orientation: portrait), (min-width: 950px) and (orientation: landscape){.navigation-menu__close-button{display:none}.navigation-menu__icon-button{grid-template-columns:24px 1fr;grid-template-rows:24px 2px;gap:2px 0px;align-items:center;padding:8px var(--space-s)}.navigation-menu__icon-button .navigation-menu__icon-button__label{margin-left:var(--space-xs)}}";

const Fragment = (_props, children) => children;
const NavigationMenu = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    /**
     * Side with which the menu is aligned with the menu button
     */
    this.direction = 'right';
    /**
     * Flag indicating if the menuButtonIcon and menuButtonLable should be visible instead of the burger menu button
     */
    this.menuButtonShow = false;
    /**
     * Label of the button to open the menu
     */
    this.menuButtonLabel = 'Navigation menu';
    this.menuButtonLabelShow = true;
    this.menuCardTitle = 'Menu';
    this.navigationItems = [];
    this.notification = false;
    this.menuFooterLinks = [];
    this.menuFooterLinksIndex = -1;
    this.isMenuOpen = false;
    this.isMenuOnMobile = false;
    this.initialNavigationItems = [...this.navigationItems];
    /**
     * Goal: Insert the footer links at a given position into the navigation menu
     * without mutating the original list.
     *
     * Default: Insert right before the last element which is usually the logout action
     */
    this.navigationItemsWithFooterLinks = [
      ...this.navigationItems.slice(0, this.menuFooterLinksIndex),
      ...this.menuFooterLinks,
      ...this.navigationItems.slice(this.menuFooterLinksIndex),
    ];
    this.menuMediaQuery = window.matchMedia('(max-width: 767px) and (orientation: portrait), (max-width: 949px) and (orientation: landscape)');
    this.toggleMenu = () => (this.isMenuOpen ? this.hideMenu() : this.showMenu());
    this.hideMenu = () => {
      this.isMenuOpen && this.handleMenuAnalytics && this.handleMenuAnalytics(false);
      this.isMenuOpen = false;
    };
    this.showMenu = () => {
      !this.isMenuOpen && this.handleMenuAnalytics && this.handleMenuAnalytics(true);
      this.isMenuOpen = true;
    };
    this.checkMediaQuery = () => {
      if (this.menuMediaQuery.matches) {
        this.isMenuOnMobile = true;
        this.navigationItems = this.navigationItemsWithFooterLinks;
      }
    };
    this.handleMenuItemKeyDown = (event, index) => {
      const { menuListElement } = this;
      const selectedListElement = event.target.parentElement;
      const firstMenuItem = menuListElement.firstElementChild
        .firstElementChild;
      const lastMenuItem = menuListElement.lastElementChild
        .lastElementChild;
      if (KEY_EVENTS.isDown(event)) {
        event.preventDefault();
        // we've reached the last anchor element
        if (index === this.itemIndex.length - 1) {
          firstMenuItem.focus();
        }
        else {
          selectedListElement.nextElementSibling.firstElementChild.focus();
        }
      }
      if (KEY_EVENTS.isUp(event)) {
        event.preventDefault();
        // select previous anchor element until we reach the first one
        if (!!index) {
          selectedListElement.previousElementSibling.firstElementChild.focus();
        }
        else {
          lastMenuItem.focus();
        }
      }
      if (KEY_EVENTS.isEsc(event)) {
        event.preventDefault();
        const menuButton = this.menuContainerElement
          .firstElementChild;
        menuButton.focus();
      }
      if (KEY_EVENTS.isEnter(event)) {
        requestAnimationFrame(() => this.hideMenu());
      }
    };
    this.handleMenuButtonKeyDown = (event) => {
      if (KEY_EVENTS.isEsc(event)) {
        this.hideMenu();
      }
    };
    this.renderNavigationItem = (item, index, isSubItem = false) => {
      const { router } = this;
      let Component = undefined;
      let props = {
        onKeyDown: (event) => this.handleMenuItemKeyDown(event, this.itemIndex.findIndex((value) => value === index)),
        onMouseUp: () => this.hideMenu(),
      };
      if ('fn' in item) {
        Component = 'button';
        props = {
          ...props,
          onKeyDown: (event) => {
            if (KEY_EVENTS.isEnter(event)) {
              this.handleNavigationItemAnalytics &&
                item.trackingEvent &&
                this.handleNavigationItemAnalytics(item.trackingEvent);
              item.fn();
            }
            this.handleMenuItemKeyDown(event, this.itemIndex.findIndex((value) => value === index));
          },
          onMouseUp: () => {
            this.handleNavigationItemAnalytics &&
              item.trackingEvent &&
              this.handleNavigationItemAnalytics(item.trackingEvent);
            item.fn();
            this.hideMenu();
          },
          class: 'u-button-reset navigation-menu__button-link',
        };
      }
      else if (item.internal) {
        Component = 'a';
        props = {
          ...props,
          class: 'navigation-menu__internal-link',
          ...href(item.route, router),
          ...(this.handleNavigationItemAnalytics &&
            item.trackingEvent && {
            onClick: (ev) => {
              ev.preventDefault();
              this.handleNavigationItemAnalytics(item.trackingEvent);
              router.push(item.route);
            },
          }),
        };
      }
      else {
        Component = 'a';
        props = {
          ...props,
          href: item.route,
          target: item.target,
          rel: item.target === '_blank' && `noreferrer noopener`,
          ...(this.handleNavigationItemAnalytics &&
            item.trackingEvent && {
            onClick: () => this.handleNavigationItemAnalytics(item.trackingEvent),
          }),
        };
      }
      return (h("li", { role: "menuitem", class: `${isSubItem ? 'navigation-menu__sub-item' : ''}` }, h(Component, { ...props }, item.icon && !item.iconSVG && (h("d4l-icon", { iconName: item.icon, iconClasses: `navigation-menu__sub-item__icon ${item.iconClasses}` })), !item.icon && item.iconSVG && (h("div", { innerHTML: item.iconSVG, class: `navigation-menu__sub-item__icon ${item.iconClasses}` })), h("div", { class: `navigation-menu__link-container ${item.icon || item.iconSVG
          ? ''
          : 'navigation-menu__link-container--no-left-margin'}
            ${!item.icon && !item.iconSVG
          ? 'navigation-menu__link-container--no-icon'
          : ''}` }, isSubItem ? (h("p", null, item.text)) : (h("span", { class: "navigation-menu__link-text" }, item.text))), Component !== 'button' && (h("div", { class: "u-margin-left--auto" }, h("d4l-icon-arrow-forward-ios", { classes: "icon--small" }))))));
    };
  }
  componentWillLoad() {
    this.checkMediaQuery();
  }
  componentWillUpdate() {
    this.checkMediaQuery();
  }
  handleWindowResize() {
    if (this.menuMediaQuery.matches) {
      this.isMenuOnMobile = true;
      this.navigationItems = this.navigationItemsWithFooterLinks;
    }
    else {
      this.isMenuOnMobile = false;
      this.navigationItems = this.initialNavigationItems;
    }
  }
  handleDocumentClick(event) {
    const { menuContainerElement, hideMenu } = this;
    if (menuContainerElement &&
      menuContainerElement !== event.target &&
      !menuContainerElement.contains(event.target)) {
      hideMenu();
    }
  }
  get itemIndex() {
    return [].concat(...this.navigationItems.map((item, itemIndex) => [
      `${itemIndex}`,
      ...(item.subItems
        ? item.subItems.map((_subItem, subItemIndex) => `${itemIndex}-${subItemIndex}`)
        : []),
    ]));
  }
  render() {
    const { classes, direction, menuButtonShow, menuButtonIcon, menuButtonLabel, menuButtonLabelShow, menuCardTitle, navigationItems, isMenuOpen, isMenuOnMobile, notification, supportedLanguages, selectedLanguage, menuFooterLinks, toggleMenu, handleMenuButtonKeyDown, router, } = this;
    return (h("div", { class: `navigation-menu ${classes}`, ref: (el) => (this.menuContainerElement = el) }, h("button", { class: "u-button-reset", "aria-expanded": isMenuOpen.toString(), "aria-haspopup": "true", type: "button", onClick: () => toggleMenu(), onKeyDown: (event) => handleMenuButtonKeyDown(event), title: menuButtonLabel }, notification && h("div", { class: "navigation-menu__dot" }), menuButtonShow ? (h("div", { class: `navigation-menu__icon-button ${!menuButtonLabelShow ? 'navigation-menu__icon-button--no-label' : ''}` }, menuButtonIcon && h("d4l-icon", { iconName: menuButtonIcon }), menuButtonLabelShow && (h("div", { class: "navigation-menu__icon-button__label" }, menuButtonLabelShow && menuButtonLabel)))) : (h(Fragment, null, h("span", { class: "navigation-menu__burger" }), h("span", { class: "navigation-menu__burger" }), h("span", { class: "navigation-menu__burger navigation-menu__burger--no-margin" }), h("span", { class: "u-visually-hidden" }, menuButtonLabel)))), h("div", { class: `navigation-menu__card
               ${direction === 'left'
        ? 'navigation-menu__card--left-aligned'
        : 'navigation-menu__card--right-aligned'}` }, h("d4l-card", { classes: "card--desktop-round-corners-m card--no-padding card--sharp-corners card--desktop" }, h("div", { slot: "card-header", class: "navigation-menu__header" }, h("span", null, menuCardTitle), supportedLanguages && (h("d4l-language-switcher", { "data-test": "languageSwitcher", languages: supportedLanguages, activeLanguage: selectedLanguage })), h("button", { class: "navigation-menu__close-button", "aria-expanded": isMenuOpen.toString(), type: "button", onClick: () => toggleMenu(), onKeyDown: (event) => handleMenuButtonKeyDown(event), title: menuButtonLabel }, h("d4l-icon-close", { classes: "icon--small" }))), h("div", { slot: "card-content", class: `${menuFooterLinks && !!menuFooterLinks.length
        ? 'navigation-menu__content'
        : 'navigation-menu__content--padded'}` }, h("ul", { class: "u-list-reset", role: "menu", ref: (el) => (this.menuListElement = el) }, navigationItems
      .filter(({ condition }) => condition !== undefined ? condition : true)
      .map((item, index) => (h(Fragment, null, this.renderNavigationItem(item, `${index}`), item.subItems &&
      item.subItems.map((subItem, subIndex) => this.renderNavigationItem(subItem, `${index}-${subIndex}`, true)))))), !!menuFooterLinks.length && !isMenuOnMobile && (h("ul", { class: "navigation-menu__footer u-list-reset u-padding-top--s u-padding-bottom--m u-padding-horizontal--m" }, menuFooterLinks.map((item) => {
      var _a;
      return (h("li", null, !item.internal ? (h("a", { class: "navigation-menu__footer__link", title: item.title, href: item.route, target: (_a = item.target) !== null && _a !== void 0 ? _a : '_blank', rel: item.target !== '_self' && 'noopener' }, item.text)) : (h("a", { class: "navigation-menu__footer__link", title: item.title, ...href(item.route, router) }, item.text))));
    }))))))));
  }
};
NavigationMenu.style = navigationMenuCss;

export { CompanyLogo as d4l_company_logo, NavigationMenu as d4l_navigation_menu };
