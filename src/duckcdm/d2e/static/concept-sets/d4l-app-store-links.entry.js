import { r as registerInstance, h } from './index-001d5b4b.js';

const appStoreLinksCss = ".app-store-links.sc-d4l-app-store-links{display:flex;flex-flow:row nowrap}.app-store-link.sc-d4l-app-store-links{display:block;flex:none;padding:8px}";

var ICON_LANGUAGES;
(function (ICON_LANGUAGES) {
  ICON_LANGUAGES["DE"] = "de";
  ICON_LANGUAGES["EN"] = "en";
})(ICON_LANGUAGES || (ICON_LANGUAGES = {}));
const AppStoreLinks = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.iconHeight = 32;
    this.language = ICON_LANGUAGES.EN;
  }
  render() {
    const { classes, iconHeight, language, linkAndroid, linkIos, textAndroid, textIos, handleClickAndroid, handleClickIos, } = this;
    return (h("div", { role: "navigation", class: `app-store-links ${classes}` }, h("a", { class: "app-store-link", href: linkAndroid, title: textAndroid, "aria-label": textAndroid, onClick: handleClickAndroid, rel: "noopener noreferer", target: "_blank" }, h("d4l-icon-appstore-android", { language: language, height: iconHeight })), h("a", { class: "app-store-link", href: linkIos, title: textIos, "aria-label": textIos, onClick: handleClickIos, rel: "noopener noreferer", target: "_blank" }, h("d4l-icon-appstore-ios", { language: language, height: iconHeight }))));
  }
};
AppStoreLinks.style = appStoreLinksCss;

export { AppStoreLinks as d4l_app_store_links };
