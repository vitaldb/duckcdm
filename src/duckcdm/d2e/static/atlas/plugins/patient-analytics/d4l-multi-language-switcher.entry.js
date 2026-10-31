import { r as registerInstance, c as createEvent, h } from './index-001d5b4b.js';
import { K as KEY_EVENTS } from './constants-c55fb626.js';

const multiLanguageSwitcherCss = ".multi-language-switcher__container.sc-d4l-multi-language-switcher{height:40px;position:relative;width:88px}.multi-language-switcher__button.sc-d4l-multi-language-switcher{align-items:center;background:none;border-radius:8px;border:1px solid var(--color-primary);color:var(--color-primary);cursor:pointer;display:flex;fill:var(--color-primary);font-size:14px;font-weight:500;height:100%;justify-content:space-between;margin:0;padding:8px;text-transform:uppercase;width:100%}.multi-language-switcher__button.sc-d4l-multi-language-switcher:hover{background:var(--color-primary-extra-lightest)}.multi-language-switcher__button.sc-d4l-multi-language-switcher:active,.multi-language-switcher__button--active.sc-d4l-multi-language-switcher{background:var(--color-primary);color:white;fill:white}.multi-language-switcher__button--active.sc-d4l-multi-language-switcher:hover{background:var(--color-primary-light)}.multi-language-switcher__globe.sc-d4l-multi-language-switcher{height:20px;width:20px}.multi-language-switcher__chevron.sc-d4l-multi-language-switcher{height:13px;width:13px}.multi-language-switcher__button--active.sc-d4l-multi-language-switcher .multi-language-switcher__chevron.sc-d4l-multi-language-switcher{transform:rotate(180deg)}.multi-language-switcher__option-list.sc-d4l-multi-language-switcher{background:white;border-radius:4px;border:1px solid var(--color-primary);display:none;list-style:none;margin:4px 0 0;max-height:134px;overflow:hidden auto;padding:0;position:absolute;top:100%;width:240px}.multi-language-switcher__option-list--right.sc-d4l-multi-language-switcher{right:0}.multi-language-switcher__option-list--open.sc-d4l-multi-language-switcher{display:block}.multi-language-switcher__option.sc-d4l-multi-language-switcher{cursor:pointer;height:32px;line-height:32px;padding:0 0 0 35px;width:100%}.multi-language-switcher__option-code.sc-d4l-multi-language-switcher{text-transform:uppercase}.multi-language-switcher__option--active.sc-d4l-multi-language-switcher d4l-icon-check.sc-d4l-multi-language-switcher{align-items:center;display:flex;height:35px;justify-content:center;width:35px}.multi-language-switcher__option--active.sc-d4l-multi-language-switcher{display:flex;padding:0}.multi-language-switcher__option--focused.sc-d4l-multi-language-switcher{background:var(--color-primary-extra-lightest)}";

const MultiLanguageSwitcher = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.changeLanguage = createEvent(this, "changeLanguage", 7);
    this.classes = '';
    this.languages = [];
    this.listboxPosition = 'left';
    this.label = 'Choose a language';
    this.isListboxOpen = false;
    this.focusedOptionIndex = 0;
    this.focusShouldResetToButton = false;
    this.resetFocusedOptionIndex();
  }
  async changeLanguageHandler(language) {
    this.changeLanguage.emit(language);
    this.hideListbox();
    return language !== this.activeLanguage;
  }
  handleDocumentClick(event) {
    const { container } = this;
    if (container &&
      container !== event.target &&
      !container.contains(event.target)) {
      this.hideListbox();
    }
  }
  componentDidUpdate() {
    if (this.isListboxOpen) {
      this.focusListbox();
    }
  }
  toggleListbox() {
    this.isListboxOpen ? this.hideListbox() : this.showListbox();
  }
  showListbox() {
    this.isListboxOpen = true;
    this.focusShouldResetToButton = this.button === document.activeElement;
  }
  hideListbox() {
    this.isListboxOpen = false;
    this.resetFocusedOptionIndex();
    if (this.focusShouldResetToButton) {
      this.focusButton();
      this.focusShouldResetToButton = false;
    }
  }
  focusListbox() {
    this.listbox.focus();
  }
  focusButton() {
    this.button.focus();
  }
  resetFocusedOptionIndex() {
    this.focusedOptionIndex = this.languages.findIndex((language) => language === this.activeLanguage);
  }
  checkShowListbox(event) {
    if (KEY_EVENTS.isUp(event) || KEY_EVENTS.isDown(event)) {
      event.preventDefault();
      this.showListbox();
    }
  }
  handleKeyboardSelection(event) {
    const ul = this.listbox;
    if (ul !== undefined) {
      if (KEY_EVENTS.isHome(event)) {
        event.preventDefault();
        this.focusedOptionIndex = 0;
      }
      else if (KEY_EVENTS.isEnd(event)) {
        event.preventDefault();
        this.focusedOptionIndex = this.languages.length - 1;
      }
      else if (KEY_EVENTS.isUp(event)) {
        event.preventDefault();
        this.focusedOptionIndex =
          this.focusedOptionIndex === 0
            ? this.languages.length - 1
            : this.focusedOptionIndex - 1;
      }
      else if (KEY_EVENTS.isDown(event)) {
        event.preventDefault();
        this.focusedOptionIndex =
          this.focusedOptionIndex >= this.languages.length - 1
            ? 0
            : this.focusedOptionIndex + 1;
      }
      else if (KEY_EVENTS.isSpace(event) || KEY_EVENTS.isEnter(event)) {
        event.preventDefault();
        this.changeLanguageHandler(this.languages[this.focusedOptionIndex]);
        this.hideListbox();
      }
      else if (KEY_EVENTS.isEsc(event)) {
        event.preventDefault();
        this.hideListbox();
      }
    }
  }
  preventTabbingOut(event) {
    if (KEY_EVENTS.isTab(event)) {
      event.preventDefault();
    }
  }
  onSelectOption(event, language) {
    event.preventDefault();
    this.changeLanguageHandler(language);
  }
  focusOptionIndex(index) {
    this.focusedOptionIndex = index;
  }
  render() {
    const { activeLanguage, classes, focusedOptionIndex, isListboxOpen, languages, listboxPosition, } = this;
    const activeDescendantId = `multi-language-switcher__option-${languages[focusedOptionIndex].code}`;
    return (h("div", { class: `multi-language-switcher__container ${classes}`, ref: (container) => (this.container = container) }, h("span", { id: "language-switcher-label-prefix", class: "u-visually-hidden", "aria-hidden": "true" }, this.label), h("button", { "aria-expanded": `${isListboxOpen}`, "aria-haspopup": "listbox", "aria-labelledby": "language-switcher-label-prefix multi-language-switcher__button", class: `multi-language-switcher__button ${isListboxOpen ? 'multi-language-switcher__button--active' : ''}`, id: "multi-language-switcher__button", onClick: () => this.toggleListbox(), onKeyUp: (event) => this.checkShowListbox(event), type: "button", ref: (button) => (this.button = button) }, h("d4l-icon-i18n", { class: "multi-language-switcher__globe", classes: "icon--size-auto icon--current-color" }), activeLanguage === null || activeLanguage === void 0 ? void 0 :
      activeLanguage.code, h("d4l-icon-arrow", { class: "multi-language-switcher__chevron", classes: "icon--size-auto icon--current-color" })), h("ul", { "aria-activedescendant": activeDescendantId, "aria-labelledby": "multi-language-switcher__button", class: `multi-language-switcher__option-list ${isListboxOpen ? 'multi-language-switcher__option-list--open' : ''} ${listboxPosition === 'right'
        ? 'multi-language-switcher__option-list--right'
        : ''}`, onKeyDown: (event) => this.preventTabbingOut(event), onKeyUp: (event) => this.handleKeyboardSelection(event), ref: (ul) => (this.listbox = ul), role: "listbox", tabindex: "-1" }, languages.map((language, index) => {
      const isOptionActive = activeLanguage === language;
      const isOptionFocused = index === focusedOptionIndex;
      return (h("li", { "aria-selected": '' + isOptionActive, class: `multi-language-switcher__option ${isOptionFocused ? 'multi-language-switcher__option--focused' : ''} ${isOptionActive ? 'multi-language-switcher__option--active' : ''}`, id: `multi-language-switcher__option-${language.code}`, onClick: (event) => this.onSelectOption(event, language), onMouseEnter: () => this.focusOptionIndex(index), role: "option" }, isOptionActive && h("d4l-icon-check", { classes: "icon--small" }), h("span", { lang: language.code }, language.label), language.label && h("span", null, "\u00A0-\u00A0"), h("span", { class: "multi-language-switcher__option-code" }, language.code)));
    }))));
  }
};
MultiLanguageSwitcher.style = multiLanguageSwitcherCss;

export { MultiLanguageSwitcher as d4l_multi_language_switcher };
