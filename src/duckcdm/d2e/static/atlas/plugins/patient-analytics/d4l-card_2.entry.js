import { r as registerInstance, h, c as createEvent } from './index-001d5b4b.js';

const cardCss = ".card.sc-d4l-card{border-radius:var(--border-radius-medium, var(--border-radius-s));color:var(--color-primary);--card-default-padding:1em 1.5em 1.75em;--card-default-background-color:#fff;--card-default-box-shadow:var(--shadow-s)}.card--sharp-corners.sc-d4l-card{border-radius:0}.card--round-corners-s.sc-d4l-card{border-radius:var(--border-radius-xs)}.card--round-corners-l.sc-d4l-card{border-radius:var(--border-radius-m)}.card--box-shadow.sc-d4l-card{box-shadow:var(--shadow-s);background:#fff}.card--text-center.sc-d4l-card{text-align:center}.card--clickable.sc-d4l-card{cursor:pointer;padding:1em 1.5em;transition:box-shadow 0.2s}.card--desktop.sc-d4l-card{padding:var(--card-default-padding);background-color:var(--card-default-background-color);box-shadow:var(--card-default-box-shadow)}.card--clickable.sc-d4l-card:focus,.card--clickable.sc-d4l-card:hover{outline:none;box-shadow:var(--shadow-m)}.card.card--no-padding.sc-d4l-card{padding:0}.card--overflow-hidden.sc-d4l-card{overflow:hidden}.card--sticky-footer.sc-d4l-card .card__footer.sc-d4l-card{position:sticky;bottom:0;z-index:var(--z-index-sticky-card-footer);background-color:white;border-bottom-left-radius:var(--border-radius-xl);border-bottom-right-radius:var(--border-radius-xl);border-top:1px solid var(--color-primary-extra-lightest)}@media screen and (min-width: 768px){.card.sc-d4l-card{padding:var(--card-default-padding);background-color:var(--card-default-background-color);box-shadow:var(--card-default-box-shadow)}.card--desktop-round-corners-m.sc-d4l-card{border-radius:var(--border-radius-m)}.card--sticky-footer.sc-d4l-card .card__footer.sc-d4l-card{border-top:0}}";

const Card = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
  }
  onKeyDown(event) {
    const { key } = event;
    (key === 'Enter' || key === ' ') && this.handleClick(event);
  }
  render() {
    const { classes, handleClick } = this;
    return (h("div", { class: `card ${classes} ${handleClick ? 'card--clickable' : ''}`, tabIndex: handleClick ? 0 : null, role: handleClick ? 'button' : null, onClick: handleClick, onKeyDown: handleClick && (event => this.onKeyDown(event)) }, h("div", { class: "card__header" }, h("slot", { name: "card-header" })), h("div", { class: "card__content" }, h("slot", { name: "card-content" })), h("div", { class: "card__footer" }, h("slot", { name: "card-footer" }))));
  }
};
Card.style = cardCss;

const languageSwitcherCss = ".language-switcher.sc-d4l-language-switcher{display:flex;flex-flow:row nowrap;font-weight:400;font-size:15px;color:var(--color-primary)}.language-switcher__item.sc-d4l-language-switcher{flex:none}.language-switcher__item.sc-d4l-language-switcher+.language-switcher__item.sc-d4l-language-switcher::before{content:'\\a0/\\a0'}.language-switcher__button.sc-d4l-language-switcher{display:inline-block;background:transparent;padding:0.5em 0;border:0 none;text-transform:uppercase;cursor:pointer;font-size:inherit;font-family:inherit;font-weight:inherit;color:inherit}.language-switcher__item--active.sc-d4l-language-switcher .language-switcher__button.sc-d4l-language-switcher{font-weight:500}";

const LanguageSwitcher = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.changeLanguage = createEvent(this, "changeLanguage", 7);
    this.classes = '';
    this.languages = [];
  }
  async changeLanguageHandler(language) {
    this.changeLanguage.emit(language);
    return language !== this.activeLanguage;
  }
  render() {
    const { classes, languages, activeLanguage } = this;
    return (h("nav", { class: `language-switcher ${classes}` }, languages.map(language => {
      const { text, code, label } = language;
      const isActive = activeLanguage === language;
      return (h("div", { class: `language-switcher__item ${isActive ? 'language-switcher__item--active' : ''}` }, h("button", { class: "language-switcher__button", type: "button", onClick: event => {
          event.preventDefault();
          this.changeLanguageHandler(language);
        }, "aria-label": label, "aria-current": isActive, title: label }, text || code)));
    })));
  }
};
LanguageSwitcher.style = languageSwitcherCss;

export { Card as d4l_card, LanguageSwitcher as d4l_language_switcher };
