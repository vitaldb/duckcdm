import { r as registerInstance, c as createEvent, h, g as getElement } from './index-001d5b4b.js';

const dateInputCss = ".fieldset.sc-d4l-date-input{min-width:0;margin:0;padding:0;border:0}.fieldset.sc-d4l-date-input>legend.sc-d4l-date-input{padding:0}.fieldset__row.sc-d4l-date-input::after,.fieldset__item.sc-d4l-date-input::after{content:'';display:block;clear:both}.fieldset__item.sc-d4l-date-input{display:inline-block;margin-right:20px;margin-bottom:0;position:relative}.fieldset__item.sc-d4l-date-input label.sc-d4l-date-input{display:block}.date-input-datepicker.sc-d4l-date-input{display:block;position:relative;overflow:hidden;margin:1rem auto 0}.date-input-datepicker__input.sc-d4l-date-input,.date-input-datepicker__input.sc-d4l-date-input::-webkit-calendar-picker-indicator{position:absolute;left:0;top:0;height:100%;width:100%;margin:0;padding:0;box-sizing:border-box;cursor:pointer}.date-input-datepicker__input.sc-d4l-date-input{z-index:1;opacity:0;width:50px}.date-input-datepicker__input.sc-d4l-date-input::-webkit-calendar-picker-indicator{z-index:2;opacity:0}@media screen and (min-width: 400px){.date-input-datepicker.sc-d4l-date-input{display:inline-block;vertical-align:middle;margin:0.5rem 0}}";

const DateInput = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.dateChange = createEvent(this, "dateChange", 7);
    this.classes = '';
    this.fields = {
      day: { label: 'Day' },
      month: { label: 'Month' },
      year: { label: 'Year' },
    };
    this.order = ['day', 'month', 'year'];
    this.errorMessage = 'Please enter a valid date';
    this.enableDatePicker = false;
    this.futureAllowed = true;
    this.pastAllowed = true;
    this.hiddenLabels = true;
    this.required = true;
    this.datePickerText = 'Open a date picker';
    this.shouldValidate = true;
    this.lastValidDate = '';
    this.onFocus = (event) => {
      const value = event.target.value;
      if (value && this.shouldValidate) {
        this.showErrorMessage(event.target);
      }
    };
    this.handleDatePickerInput = (event) => {
      const { order, host } = this;
      const input = event.target;
      const [year = '', month = '', day = ''] = input.value.split('-');
      const inputElements = host.querySelectorAll('input');
      const values = { year, month, day };
      order.forEach((key) => (inputElements[order.indexOf(key)].value = values[key]));
      this.handleInput();
    };
    this.emitChange = (date) => {
      this.handleChange && typeof this.handleChange === 'function'
        ? this.handleChange(date)
        : this.dateChangeHandler(date);
    };
    this.handleInput = () => {
      var _a;
      const { order, host } = this;
      this.errorAt = -1;
      host
        .querySelectorAll('input')
        .forEach((input) => this.setErrorMessage(input, true));
      const values = [
        ...Array.prototype.slice.call(host.querySelectorAll('input[type="text"]')),
      ].map((input) => input.value === '' ? null : parseInt(input.value, 10));
      const yearIndex = order.findIndex((value) => value === 'year');
      const monthIndex = order.findIndex((value) => value === 'month');
      const dayIndex = order.findIndex((value) => value === 'day');
      const year = values[yearIndex];
      const month = monthIndex > -1
        ? values[monthIndex] !== null
          ? values[monthIndex] - 1
          : null
        : 0;
      const day = dayIndex > -1 ? values[dayIndex] : 1;
      const isYearActiveElement = ((_a = document.activeElement) === null || _a === void 0 ? void 0 : _a.id.indexOf(order[yearIndex])) > -1;
      if (isYearActiveElement && (year === null || year === void 0 ? void 0 : year.toString().length) < 4) {
        this.emitChange(undefined);
        return;
      }
      if (this.validDay(day, dayIndex) &&
        this.validMonth(month, monthIndex) &&
        this.validYear(year, yearIndex) &&
        this.validDate(day, month, year, values)) {
        const date = `${year}-${this.zeroPadded(month + 1)}-${this.zeroPadded(day)}`;
        this.emitChange(date);
        this.lastValidDate = date;
      }
      else {
        this.emitChange(undefined);
      }
      this.shouldValidate &&
        this.showErrorMessage(document.activeElement);
    };
    this.zeroPadded = (value) => `${('0' + value).slice(-2)}`;
    this.inFuture = (date) => date.setHours(0, 0, 0, 0) > new Date().setHours(0, 0, 0, 0);
    this.inPast = (date) => date.setHours(0, 0, 0, 0) < new Date().setHours(0, 0, 0, 0);
    this.getPattern = (key) => (key === 'year' ? '[0-9]{4}' : '[0-9]{0,2}');
    this.getInput = (key, field, index, classes = 'input--small') => {
      return (h("div", { class: "fieldset__item" }, h("d4l-input", { inputId: `${key}__${index}`, classes: `${classes} input--center`, label: field.label, type: "text", pattern: this.getPattern(key), inputmode: "numeric", required: this.required, onInput: this.handleInput, error: this.errorAt === index || this.errorAt === -2, placeholder: field.placeholder, hiddenlabel: this.hiddenLabels, handleFocus: this.onFocus, value: field.value })));
    };
  }
  dateChangeHandler(value) {
    this.dateChange.emit({ value });
  }
  get canEnableDatePicker() {
    const input = document.createElement('input');
    input.type = 'date';
    input.value = 'invalid date';
    const supportsNativeDate = input.value !== 'invalid date';
    return (supportsNativeDate &&
      this.order.includes('day') &&
      this.order.includes('month') &&
      this.order.includes('year'));
  }
  validDate(day, month, year, values) {
    const date = new Date(year, month, day);
    // Check for "Invalid Date"
    if (date instanceof Date && isNaN(date.getTime())) {
      this.setErrorMessage(0, false, true);
      return false;
    }
    if (!this.shouldValidate) {
      return true;
    }
    if (values.every((value) => value !== null)) {
      // Check if valid date
      if (!(date &&
        date.getMonth() === month &&
        year &&
        year.toString().length === 4 &&
        date.getFullYear() === year) ||
        (!this.futureAllowed && this.inFuture(date)) ||
        (!this.pastAllowed && this.inPast(date)) ||
        (!!this.min && this.min.getTime() > date.getTime()) ||
        (!!this.max && this.max.getTime() < date.getTime())) {
        this.setErrorMessage(0, false, true);
        return false;
      }
      return true;
    }
    return false;
  }
  validDay(day, dayIndex) {
    if (day !== null && day !== NaN) {
      if (day.toString().length > 2 || day < 1 || day > 31) {
        this.setErrorMessage(dayIndex);
        return false;
      }
      return true;
    }
    return false;
  }
  validMonth(month, monthIndex) {
    if (month !== null && month !== NaN) {
      if (month.toString().length > 2 || month < 0 || month > 11) {
        this.setErrorMessage(monthIndex);
        return false;
      }
      return true;
    }
    return false;
  }
  validYear(year, yearIndex) {
    if (year !== null && year !== NaN) {
      if (year.toString().length !== 4) {
        this.setErrorMessage(yearIndex);
        return false;
      }
      return true;
    }
    return false;
  }
  setErrorMessage(index, clear = false, all = false) {
    try {
      const element = typeof index === 'number'
        ? this.host.querySelectorAll('input')[index]
        : index;
      element.setCustomValidity(clear ? '' : this.errorMessage);
      if (!clear && typeof index === 'number') {
        this.errorAt = all ? -2 : index;
      }
    }
    catch { }
  }
  showErrorMessage(element) {
    try {
      element.reportValidity();
    }
    catch { }
  }
  render() {
    const { classes, label, fields, order } = this;
    return (h("div", { class: `date-input ${classes}` }, h("fieldset", { class: "fieldset" }, label && h("legend", { class: "fieldset__label" }, label), h("div", { class: "fieldset__row" }, order.map((key, index, items) => this.getInput(key, fields[key], index, items.length > 1 ? 'input--small' : 'input--medium')), this.enableDatePicker && this.canEnableDatePicker && (h("div", { class: "fieldset__item date-input-datepicker" }, h("span", { class: "u-visually-hidden" }, this.datePickerText), h("input", { type: "date", class: "date-input-datepicker__input", value: this.lastValidDate, onChange: this.handleDatePickerInput, tabIndex: -1 }), h("d4l-icon-calendar", { classes: "icon--small" })))))));
  }
  get host() { return getElement(this); }
};
DateInput.style = dateInputCss;

export { DateInput as d4l_date_input };
