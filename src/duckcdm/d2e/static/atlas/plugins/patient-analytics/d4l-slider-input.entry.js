import { r as registerInstance, h } from './index-001d5b4b.js';

const sliderInputCss = "@keyframes slider_knob_pristine{0%{opacity:0;left:10%}25%{opacity:1}50%{opacity:0;left:90%}75%{opacity:1}100%{opacity:0;left:10%}}.slider-input.sc-d4l-slider-input{--slider-input-value-spacing:calc(var(--font-size-desktop-s) + var(--space-xs));display:block;height:20px;padding:0 10px;user-select:none;cursor:pointer}.slider-input--scale.sc-d4l-slider-input,.slider-input--label.sc-d4l-slider-input{margin-bottom:32px}.slider-input--scale.slider-input--label.sc-d4l-slider-input{margin-bottom:calc(1rem + var(--font-size-desktop-xs) + var(--space-m))}.slider-input__inner.sc-d4l-slider-input{position:relative;height:100%}.slider-input__inner.sc-d4l-slider-input::before{content:'';display:block;position:absolute;height:2px;left:0;width:100%;top:50%;margin-top:-1px;background:var(--color-primary-lightest);z-index:0}.slider-input__knob.sc-d4l-slider-input{position:relative;display:block;width:20px;height:20px;border-radius:50%;margin-left:-10px;cursor:pointer;background:var(--color-primary);transition:left 0.15s ease-out;will-change:left, opacity;z-index:2}.slider-input__knob.sc-d4l-slider-input::before,.slider-input__knob.sc-d4l-slider-input::after{content:'';position:absolute;display:block;border:1px solid transparent;border-radius:50%;pointer-events:none;background-color:transparent;transition:border-color 0.1s linear, background-color 0.1s linear}.slider-input__knob.sc-d4l-slider-input::before{width:16px;height:16px;left:2px;top:2px}.slider-input__knob.sc-d4l-slider-input::after{width:6px;height:6px;left:7px;top:7px}.slider-input__knob.sc-d4l-slider-input:hover::before,.slider-input--focused.sc-d4l-slider-input .slider-input__knob.sc-d4l-slider-input::before,.slider-input__knob--dragging.sc-d4l-slider-input::before{border-color:#fff}.slider-input__knob--dragging.sc-d4l-slider-input::after{background-color:#fff}.slider-input__knob--pristine.sc-d4l-slider-input{animation:slider_knob_pristine 8s ease-in-out infinite}.slider-input__input.sc-d4l-slider-input{top:0;position:absolute;opacity:0;pointer-events:none}.slider-input__value.sc-d4l-slider-input{position:absolute;left:50%;bottom:100%;margin-bottom:var(--space-xs);font-size:var(--font-size-desktop-s);line-height:1;transform:translateX(-50%);color:var(--color-primary)}.slider-input__scale.sc-d4l-slider-input{position:absolute;height:10px;left:0;width:100%;top:50%;padding:0;margin:-5px 0 0;overflow:visible;z-index:1}.slider-input__scale-marker.sc-d4l-slider-input{position:absolute;display:block;width:2px;height:100%;margin-left:-1px;background:var(--color-primary-lightest)}.slider-input__scale-value.sc-d4l-slider-input{position:absolute;display:block;margin-top:1rem;top:100%;color:var(--color-neutral);font-size:10px;transform:translateX(-50%)}.slider-input__label.sc-d4l-slider-input{position:relative;display:flex;margin-top:0.5rem;flex-flow:row nowrap;justify-content:space-between;color:var(--color-neutral);font-size:var(--font-size-desktop-xs)}.slider-input--scale.sc-d4l-slider-input .slider-input__label.sc-d4l-slider-input{margin:calc(0.5rem + var(--space-m)) -8px 0}.slider-input--disabled.sc-d4l-slider-input{cursor:not-allowed}.slider-input--disabled.sc-d4l-slider-input .slider-input__knob.sc-d4l-slider-input{cursor:not-allowed;background:var(--color-neutral-light)}.slider-input--disabled.sc-d4l-slider-input .slider-input__knob.sc-d4l-slider-input:hover::before,.slider-input--disabled.sc-d4l-slider-input .slider-input--focused.sc-d4l-slider-input .slider-input__knob.sc-d4l-slider-input::before,.slider-input--disabled.sc-d4l-slider-input .slider-input__knob--dragging.sc-d4l-slider-input::before{border-color:var(--color-neutral-light)}.slider-value.sc-d4l-slider-input{padding:0 10px;height:25px}.slider-value.sc-d4l-slider-input span.sc-d4l-slider-input{position:relative;transition:left 0.15s ease-out;will-change:left;color:var(--color-primary)}";

const MAX_PRECISION = 1;
const SliderInput = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.step = 1;
    this.scale = false;
    this.ticks = false;
    this.compact = false;
    this.disabled = false;
    this.showValue = false;
    this.locale = navigator.language;
    this.focused = false;
    this.dragging = false;
    this.startDrag = this.startDrag.bind(this);
    this.drag = this.drag.bind(this);
    this.endDrag = this.endDrag.bind(this);
    this.point = this.point.bind(this);
    this.onInputChange = this.onInputChange.bind(this);
  }
  changeValue(value) {
    this.inputValue = value;
  }
  get steps() {
    const { min, max, step } = this;
    return parseInt(((max - min) / step).toFixed(0)) + 1;
  }
  get values() {
    const { min, step, steps } = this;
    return new Array(steps)
      .fill(null)
      .map((_, index) => parseFloat((index * step + min).toFixed(MAX_PRECISION)));
  }
  get scaleEl() {
    const { scale, ticks, values, compact } = this;
    if (!ticks) {
      return null;
    }
    const steps = values.length;
    return (h("legend", { class: "slider-input__scale" }, values.map((value, index, arr) => (!compact || !index || index === arr.length - 1) && (h("div", { key: index }, h("span", { class: "slider-input__scale-marker", style: { left: `${(index / (steps - 1)) * 100}%` } }), scale && (h("span", { class: "slider-input__scale-value", style: { left: `${(index / (steps - 1)) * 100}%` } }, value)))))));
  }
  get labelEl() {
    const { minLabel, maxLabel } = this;
    if (!minLabel && !maxLabel) {
      return null;
    }
    return (h("div", { class: "slider-input__label" }, h("span", { class: "slider-input__label-item" }, minLabel), h("span", { class: "slider-input__label-item" }, maxLabel)));
  }
  get knobPosition() {
    const index = this.values.indexOf(this.inputValue);
    if (index === -1) {
      return null;
    }
    return `${(index / (this.steps - 1)) * 100}%`;
  }
  get inputStartingValue() {
    return String(this.values.slice(0, 2).slice(-1).pop());
  }
  get isPristine() {
    return !this.values.includes(this.inputValue);
  }
  getX(event) {
    const coords = 'changedTouches' in event ? event.changedTouches[0] : event;
    const { clientX } = coords || {};
    return clientX;
  }
  startDrag(event) {
    event.stopPropagation();
    event.preventDefault();
    if (this.disabled) {
      return;
    }
    const { left, right } = this.sliderInnerEl.getBoundingClientRect();
    this.xStepWidth = (right - left) / (this.steps - 1);
    this.xStart = left;
    document.addEventListener('mouseup', this.endDrag);
    document.addEventListener('touchend', this.endDrag);
    document.addEventListener('mousemove', this.drag);
    document.addEventListener('touchmove', this.drag);
    this.dragging = true;
  }
  drag(event) {
    event.preventDefault();
    if (this.disabled) {
      return;
    }
    const { xStart, xStepWidth, steps } = this;
    const x = this.getX(event);
    const stepIndex = Math.min(Math.max(Math.round((x - xStart) / xStepWidth), 0), steps - 1);
    const newValue = this.values[stepIndex];
    if (newValue === this.inputValue) {
      return;
    }
    this.inputValue = this.values[stepIndex];
    this.sliderInputEl.value = String(this.inputValue);
    this.sliderInputEl.dispatchEvent(new Event('change'));
  }
  endDrag(event) {
    event.preventDefault();
    if (this.disabled) {
      return;
    }
    document.removeEventListener('mouseup', this.endDrag);
    document.removeEventListener('touchend', this.endDrag);
    document.removeEventListener('mousemove', this.drag);
    document.removeEventListener('touchmove', this.drag);
    this.dragging = false;
    setTimeout(() => this.sliderInputEl.blur(), 0);
  }
  point(event) {
    if (this.disabled) {
      return;
    }
    this.startDrag(event);
    this.drag(event);
  }
  onInputChange(event) {
    var _a;
    const target = event.target;
    const value = parseFloat(target.value);
    this.inputValue !== value && (this.inputValue = value);
    (_a = this.handleChange) === null || _a === void 0 ? void 0 : _a.call(this, {
      ...event,
      target: { ...target, value },
    });
  }
  componentWillLoad() {
    this.ticks = this.scale || this.ticks;
    this.min = parseFloat(this.min.toFixed(MAX_PRECISION));
    this.max = parseFloat(this.max.toFixed(MAX_PRECISION));
    this.step = parseFloat(this.step.toFixed(MAX_PRECISION));
    const { min, max, step, value } = this;
    if (!!(parseFloat(((max - min) * 10).toFixed(MAX_PRECISION)) % (step * 10))) {
      throw new Error(`slider-input error: range of min ${min} and max ${max} is not divisible by step ${step}`);
    }
    this.inputValue = value;
  }
  render() {
    const { min, max, minLabel, maxLabel, step, steps, scale, compact, scaleEl, labelEl, dragging, isPristine, knobPosition, inputStartingValue, inputValue, focused, disabled, locale, showValue, } = this;
    return (h("label", { class: {
        'slider-input': true,
        'slider-input--focused': focused,
        'slider-input--scale': scale,
        'slider-input--label': !!minLabel || !!maxLabel,
        'slider-input--disabled': disabled,
      }, style: {
        minWidth: compact ? '0' : `${steps * 20}px`,
        marginTop: showValue ? 'var(--slider-input-value-spacing)' : '0',
      } }, h("div", { class: "slider-input__inner", ref: (el) => (this.sliderInnerEl = el), onMouseDown: this.point, onTouchStart: this.point }, scaleEl, h("div", { class: {
        'slider-input__knob': true,
        'slider-input__knob--dragging': dragging,
        'slider-input__knob--pristine': isPristine,
      }, onMouseDown: this.startDrag, onTouchStart: this.startDrag, style: { left: knobPosition } }, showValue && !isPristine && (h("span", { class: "slider-input__value" }, inputValue.toLocaleString(locale)))), h("input", { ref: (el) => (this.sliderInputEl = el), class: "slider-input__input", type: "range", min: min, max: max, step: step, value: isPristine ? inputStartingValue : inputValue, disabled: disabled, "aria-disabled": disabled, onChange: this.onInputChange, onFocus: () => (this.focused = true), onBlur: () => (this.focused = false) }), labelEl)));
  }
  static get watchers() { return {
    "value": ["changeValue"]
  }; }
};
SliderInput.style = sliderInputCss;

export { SliderInput as d4l_slider_input };
