import { r as registerInstance, h } from './index-001d5b4b.js';
import { K as KEY_EVENTS } from './constants-c55fb626.js';

const searchCss = ".search.sc-d4l-search{position:relative;display:flex;flex-flow:row nowrap;width:100%;position:relative;align-items:center}.search__input.sc-d4l-search{display:block;flex:1}.search__button.sc-d4l-search{position:absolute;display:block;flex:none;background:transparent;border:0 none;padding:var(--space-xs) var(--space-xs) var(--space-xs) var(--space-s);cursor:pointer;color:var(--color-primary);opacity:1;transition:opacity 0.2s ease-in-out;z-index:1}.search__button--search.sc-d4l-search{left:0}.search__button--cancel.sc-d4l-search{right:var(--space-xs);color:var(--color-neutral)}.search__button--hidden.sc-d4l-search{opacity:0;pointer-events:none}";

const Search = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.inputId = 'search';
    this.label = '';
    this.value = '';
    this.focused = false;
    this.ariaLabelSearch = 'Search';
    this.squared = false;
    this.showCancelBtn = !!this.value;
    this.onInput = this.onInput.bind(this);
    this.onKeyUp = this.onKeyUp.bind(this);
    this.onButtonClick = this.onButtonClick.bind(this);
    this.cancelSearch = this.cancelSearch.bind(this);
  }
  async getQuery() {
    const { value = '' } = this.inputElement || {};
    return this.getQueryByValue(value);
  }
  async cancelSearch() {
    const target = this.inputElement;
    if (!target.value) {
      target.blur && target.blur();
    }
    else {
      target.focus && target.focus();
    }
    target.value = '';
    this.triggerInput(target);
  }
  get inputElement() {
    return this.d4lInputElement ? this.d4lInputElement.querySelector('input') : null;
  }
  getQueryByValue(value) {
    return value
      .split(/\s/)
      .map((term) => term.toLowerCase())
      .filter((term) => term);
  }
  triggerInput(target) {
    this.onInput({
      ...new Event('input', {
        bubbles: true,
        cancelable: true,
      }),
      target,
    });
  }
  onInput(event) {
    const { target: { value }, } = event;
    event.query = this.getQueryByValue(value);
    this.showCancelBtn = !!value;
    this.handleInput && this.handleInput(event);
  }
  onKeyUp(event) {
    const { target } = event;
    if (KEY_EVENTS.isEsc(event)) {
      this.cancelSearch();
    }
    if (KEY_EVENTS.isEnter(event) && target.value) {
      event.query = this.getQueryByValue(target.value);
      this.handleSearch && this.handleSearch(event);
      target.blur && target.blur();
    }
  }
  async onButtonClick(event) {
    event.query = await this.getQuery();
    this.handleSearch && this.handleSearch(event);
  }
  render() {
    const { inputId, classes, label, value, focused, squared, onInput, onKeyUp, onButtonClick, cancelSearch, closeButtonText, handleFocus, handleBlur, showCancelBtn, } = this;
    return (h("div", { class: `search ${classes}` }, h("button", { class: "search__button search__button--search", type: "button", "aria-label": this.ariaLabelSearch, title: this.ariaLabelSearch !== 'Search' ? this.ariaLabelSearch : null, onClick: onButtonClick }, h("d4l-icon-search", { classes: "icon--extra-small" })), h("d4l-input", { "input-id": inputId, class: "search__input", classes: `input--icons ${squared ? 'input--squared' : 'input--round'}`, type: "text", value: value, autocomplete: "off", autocapitalize: "none", focused: focused, label: label, handleInput: onInput, handleKeyUp: onKeyUp, handleFocus: handleFocus, handleBlur: handleBlur, ref: (el) => (this.d4lInputElement = el) }), h("button", { class: `search__button search__button--cancel ${showCancelBtn ? '' : 'search__button--hidden'}`, type: "button", onClick: cancelSearch }, h("span", { class: "u-visually-hidden" }, closeButtonText), h("d4l-icon-close", { classes: "icon--extra-small" }))));
  }
};
Search.style = searchCss;

export { Search as d4l_search };
