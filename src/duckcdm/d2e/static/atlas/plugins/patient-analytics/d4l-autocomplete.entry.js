import { r as registerInstance, c as createEvent, h } from './index-001d5b4b.js';
import { K as KEY_EVENTS } from './constants-c55fb626.js';

const autocompleteCss = ".autocomplete.sc-d4l-autocomplete{position:relative;color:var(--color-primary)}.autocomplete.sc-d4l-autocomplete select.sc-d4l-autocomplete,.autocomplete__status-message.sc-d4l-autocomplete{height:1px;width:1px;overflow:hidden;position:absolute;clip:rect(1px, 1px, 1px, 1px)}.autocomplete.sc-d4l-autocomplete [role='listbox'].sc-d4l-autocomplete{margin:0;padding:0.5em 0;max-height:12em;width:100%;overflow-y:scroll;position:absolute;top:2.3em;list-style:none;z-index:2;box-shadow:var(--shadow-s);border-bottom-left-radius:4px;border-bottom-right-radius:4px;-webkit-overflow-scrolling:touch;background-color:#fff}.autocomplete.sc-d4l-autocomplete [role='listbox'].sc-d4l-autocomplete>li.sc-d4l-autocomplete{padding:0.5em 1em;outline:0}.autocomplete.sc-d4l-autocomplete [role='option'].sc-d4l-autocomplete:hover,.autocomplete.sc-d4l-autocomplete [role='option'][aria-selected='true'].sc-d4l-autocomplete{background-color:var(--color-neutral-lightest)}.autocomplete__drowdown-button.sc-d4l-autocomplete{position:absolute;right:0;top:-2px;padding:8px;background:none;border:0;z-index:5;cursor:pointer}.is-hidden.sc-d4l-autocomplete{display:none}.autocomplete.sc-d4l-autocomplete::after{display:block;position:absolute;content:'';right:0;width:42px;top:0;bottom:2px;background:linear-gradient(\n    to right,\n    rgba(255, 255, 255, 0) 0%,\n    #fff 20%,\n    #fff 100%\n  )}";

const Autocomplete = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.selectedValueChanged = createEvent(this, "selectedValueChanged", 7);
    this.inputId = null;
    this.classes = '';
    this.label = '';
    this.selectedOption = null;
    this.required = false;
    this.errorMessage = '';
    this.statusNoResults = 'No results';
    this.statusResultsFound = 'results found';
    this.options = [];
    this.inputFocused = false;
    this.error = false;
    this.disabled = false;
    this.inputValue = '';
    this.isMenuHidden = true;
    this.selectedValue = '';
    this.activeOptionIndex = null;
    this.filteredOptions = [];
    this.hasError = false;
    this.autocompleteOptionIdPrefix = 'autocomplete-option';
    this.resetMenuState = () => {
      this.isMenuHidden = true;
      this.filteredOptions = [];
      this.activeOptionIndex = null;
    };
    this.filterForMatches = (sanitisedInputValue, matchingOptionProperty = 'dataAlt') => this.options
      .map((option) => Object.assign(option, {
      match: option[matchingOptionProperty]
        .toString()
        .trim()
        .toLowerCase()
        .indexOf(sanitisedInputValue),
    }))
      .filter(({ match }) => match > -1)
      // prioritize matches where the first letter is the same as the input's first letter
      .sort(({ match: a }, { match: b }) => (a && !b ? 1 : !a && b ? -1 : 0))
      .map((option) => {
      delete option.match;
      return option;
    });
    this.onInputTextType = () => {
      let sanitisedInputValue = this.inputValue.trim().toLowerCase();
      if (sanitisedInputValue.length > 0) {
        this.filteredOptions = this.filterForMatches(sanitisedInputValue);
        this.isMenuHidden = false;
        this.resetAutocompleteMenuScroll();
      }
      else {
        this.selectedValue = '';
        this.selectedValueChangedHandler(null);
        this.resetMenuState();
      }
    };
    this.onInputTextDownPressed = () => {
      let sanitisedInputValue = this.inputValue.trim().toLowerCase();
      if (sanitisedInputValue.length === 0) {
        this.filteredOptions = [...this.options];
      }
      else {
        this.filteredOptions = this.filterForMatches(sanitisedInputValue, 'text');
      }
      this.activeOptionIndex = 0;
      this.isMenuHidden = false;
      this.resetAutocompleteMenuScroll();
      setTimeout(() => this.autocompleteMenuElement.querySelector('li').focus(), 0);
    };
    this.onInputTextKeyDown = (event) => {
      if (KEY_EVENTS.isTab(event)) {
        this.selectOptionOnFocusOut();
        this.resetMenuState();
      }
    };
    this.onInputTextChange = (event) => {
      this.inputValue = event.target.value;
    };
    this.onInputTextClick = () => {
      this.filteredOptions = [...this.options];
      this.isMenuHidden = false;
      this.resetAutocompleteMenuScroll(this.selectedValue);
    };
    this.onInputTextKeyUp = (event) => {
      if (KEY_EVENTS.isEsc(event) ||
        KEY_EVENTS.isUp(event) ||
        KEY_EVENTS.isLeft(event) ||
        KEY_EVENTS.isRight(event) ||
        KEY_EVENTS.isSpace(event) ||
        KEY_EVENTS.isEnter(event) ||
        KEY_EVENTS.isTab(event) ||
        KEY_EVENTS.isShift(event)) {
        return;
      }
      else if (KEY_EVENTS.isDown(event)) {
        this.onInputTextDownPressed();
        return;
      }
      this.onInputTextType();
      return;
    };
    this.onDropdownButtonClick = () => {
      this.onInputTextClick();
      this.activeOptionIndex = 0;
      setTimeout(() => {
        this.autocompleteMenuElement.querySelector('li').focus();
      }, 0);
    };
    this.selectOption = (option) => {
      this.hasError = false;
      this.d4lInputElement &&
        this.d4lInputElement.querySelector('input').setCustomValidity('');
      this.isMenuHidden = true;
      if (!option) {
        this.selectedValue = '';
        this.inputValue = '';
      }
      else {
        this.selectedValue = option.value;
        this.selectedValueChangedHandler(option.id);
        this.inputValue = option.text;
      }
    };
    this.selectOptionOnFocusOut = () => {
      const { errorMessage, filteredOptions: options, required } = this;
      const sanitisedInputValue = this.inputValue.trim().toLowerCase();
      if (sanitisedInputValue.length &&
        options.length === 1 &&
        options[0].text.trim().toLowerCase().includes(sanitisedInputValue)) {
        this.selectOption(options[0]);
      }
      if (required && this.selectedValue === '') {
        this.hasError = true;
        this.d4lInputElement.querySelector('input').setCustomValidity(errorMessage);
      }
    };
    this.onOptionUpArrow = (event) => {
      event.preventDefault();
      if (this.activeOptionIndex === 0) {
        this.resetMenuState();
        this.autoCompleteInputTextElement.focus();
      }
      else {
        this.activeOptionIndex--;
        event.target.previousElementSibling.focus();
      }
    };
    this.onOptionDownArrow = (event) => {
      event.preventDefault();
      if (this.filteredOptions.length - 1 > this.activeOptionIndex) {
        this.activeOptionIndex++;
        event.target.nextElementSibling.focus();
      }
    };
    this.onOptionEscape = () => {
      this.resetMenuState();
      this.autoCompleteInputTextElement.focus();
    };
    this.onMenuKeyDown = (event) => {
      if (this.disabled) {
        return;
      }
      if (KEY_EVENTS.isUp(event)) {
        this.onOptionUpArrow(event);
        return;
      }
      else if (KEY_EVENTS.isDown(event)) {
        this.onOptionDownArrow(event);
        return;
      }
      else if (KEY_EVENTS.isEnter(event)) {
        this.selectOption(this.filteredOptions[this.activeOptionIndex]);
        return;
      }
      else if (KEY_EVENTS.isSpace(event)) {
        this.selectOption(this.filteredOptions[this.activeOptionIndex]);
        return;
      }
      else if (KEY_EVENTS.isEsc(event)) {
        this.onOptionEscape();
        return;
      }
      else if (KEY_EVENTS.isTab(event)) {
        this.selectOptionOnFocusOut();
        this.resetMenuState();
        return;
      }
      this.autoCompleteInputTextElement.focus();
    };
    this.renderListItems = () => {
      const { selectOption, activeOptionIndex, autocompleteOptionIdPrefix, filteredOptions, } = this;
      return filteredOptions.map((option, index) => (h("li", { id: `${autocompleteOptionIdPrefix}-${index}`, tabindex: "-1", "aria-selected": (activeOptionIndex === index).toString(), role: "option", onClick: () => selectOption(option) }, option.text)));
    };
  }
  async reset() {
    this.selectOption(this.selectedOption);
  }
  onChangeSelectedOption(newValue, oldValue) {
    if ((newValue === null || newValue === void 0 ? void 0 : newValue.value) !== (oldValue === null || oldValue === void 0 ? void 0 : oldValue.value)) {
      this.selectOption(newValue);
    }
  }
  selectedValueChangedHandler(id) {
    const { selectedValue, inputId } = this;
    this.selectedValueChanged.emit({ key: id, value: selectedValue, inputId });
  }
  resetAutocompleteMenuScroll(selectedValue) {
    if (!this.autocompleteMenuElement) {
      return;
    }
    const selectedOption = selectedValue &&
      this.filteredOptions.find(({ value }) => value === selectedValue);
    let scrollTop = 0;
    window.requestAnimationFrame(() => {
      var _a, _b;
      if (selectedOption) {
        const index = this.filteredOptions.indexOf(selectedOption);
        const offset = (_b = (_a = this.autocompleteMenuElement) === null || _a === void 0 ? void 0 : _a.querySelector(`#autocomplete-option-${index}`)) === null || _b === void 0 ? void 0 : _b.offsetTop;
        scrollTop = offset ? Math.max(offset - 8, 0) : 0;
      }
      this.autocompleteMenuElement.scrollTop = scrollTop;
    });
  }
  get status() {
    return this.filteredOptions.length
      ? `${this.filteredOptions.length} ${this.statusResultsFound}`
      : this.statusNoResults;
  }
  componentWillLoad() {
    const { selectedOption } = this;
    selectedOption && this.selectOption(selectedOption);
  }
  componentDidLoad() {
    this.autoCompleteInputTextElement = this.autocompleteElement.querySelector('input[role=combobox]');
  }
  handleDocumentClick(event) {
    const { autocompleteElement } = this;
    if (autocompleteElement &&
      autocompleteElement !== event.target &&
      !autocompleteElement.contains(event.target)) {
      this.selectOptionOnFocusOut();
      this.resetMenuState();
    }
  }
  render() {
    const { inputId, classes, label, required, inputValue, options, status, selectedValue, isMenuHidden, filteredOptions, onInputTextChange, onInputTextKeyUp, onInputTextKeyDown, onInputTextClick, onDropdownButtonClick, onMenuKeyDown, statusNoResults, renderListItems, hasError, inputFocused, error, handleBlur, disabled, } = this;
    return (h("div", { class: `autocomplete ${classes}`, ref: (el) => (this.autocompleteElement = el) }, h("select", { "aria-hidden": "true", tabindex: "-1", disabled: disabled }, h("option", null, "Select"), !!options.length &&
      options.map((option) => (h("option", { value: option.value, "data-alt": option.dataAlt, selected: selectedValue == option.value }, option.text)))), h("d4l-input", { "input-id": inputId, type: "text", error: hasError || error, label: label, value: inputValue, role: "combobox", required: required, disabled: disabled, autocomplete: "off", autocapitalize: "none", "aria-autocomplete": "list", "aria-expanded": !isMenuHidden, "aria-owns": "autocomplete-options", handleInput: onInputTextChange, handleKeyUp: onInputTextKeyUp, handleKeyDown: onInputTextKeyDown, handleClick: onInputTextClick, handleBlur: handleBlur, focused: inputFocused, ref: (el) => (this.d4lInputElement = el) }), h("button", { type: "button", class: "autocomplete__drowdown-button", "aria-label": "Open dropdown menu", onClick: onDropdownButtonClick, disabled: disabled }, h("d4l-icon-arrow", { classes: "icon--extra-small" })), h("ul", { id: "autocomplete-options", role: "listbox", class: isMenuHidden && 'is-hidden', onKeyDown: onMenuKeyDown, ref: (el) => (this.autocompleteMenuElement = el) }, !!filteredOptions.length ? renderListItems() : h("li", null, statusNoResults)), h("div", { class: "autocomplete__status-message", "aria-live": "polite", role: "status" }, !isMenuHidden && status)));
  }
  static get watchers() { return {
    "selectedOption": ["onChangeSelectedOption"]
  }; }
};
Autocomplete.style = autocompleteCss;

export { Autocomplete as d4l_autocomplete };
