import { r as registerInstance, h } from './index-001d5b4b.js';

const scaleBarCss = ".scale-bar__bar.sc-d4l-scale-bar{background-color:var(--color-neutral-lightest);border-radius:4px;border:1px solid var(--color-neutral-lighter);box-sizing:content-box;height:20px;position:relative}.scale-bar__tick.sc-d4l-scale-bar{background:var(--color-neutral-lighter);bottom:0;content:'';display:block;height:3px;position:absolute;right:0;width:1px}.scale-bar__active-area.sc-d4l-scale-bar{background-color:var(--color-primary);border-radius:3px 0 0 3px;height:100%;transition:width 1000ms ease-in-out;width:0%;will-change:width}@keyframes appear{0%{opacity:0}80%{opacity:0}100%{opacity:1}}.scale-bar__value-label.sc-d4l-scale-bar{animation:appear 1200ms ease-in-out;box-sizing:border-box;color:var(--color-primary);font-family:var(--font-family-secondary);font-size:12px;font-stretch:normal;font-style:normal;font-weight:normal;height:20px;left:0;letter-spacing:normal;line-height:20px;padding:0 4px;position:absolute;top:0}.scale-bar__value-label--bright.sc-d4l-scale-bar{color:var(--color-neutral-lightest)}.scale-bar__range-label-container.sc-d4l-scale-bar{display:flex;justify-content:space-between;margin-top:4px}.scale-bar__range-label.sc-d4l-scale-bar{color:var(--color-neutral);font-family:var(--font-family-secondary);font-size:10px;font-stretch:normal;font-style:normal;font-weight:normal;letter-spacing:normal;line-height:1.8;max-width:50%}.scale-bar__range-label.sc-d4l-scale-bar:last-of-type{text-align:right}";

const ScaleBar = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.currentValue = undefined;
  }
  componentDidRender() {
    if (!this.observer) {
      const options = {
        threshold: 1.0,
      };
      if ('IntersectionObserver' in window) {
        this.observer = new window.IntersectionObserver(this.containerDidAppear.bind(this), options);
        this.observer.observe(this.container);
      }
      else {
        this.containerDidAppear();
      }
    }
  }
  disconnectedCallback() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = undefined;
    }
  }
  containerDidAppear() {
    this.currentValue = this.value;
  }
  valueLabel(valuePercentage, description) {
    const isLabelOnActiveArea = valuePercentage >= 50;
    const classes = isLabelOnActiveArea ? 'scale-bar__value-label--bright' : '';
    const styles = isLabelOnActiveArea
      ? {
        width: `${valuePercentage}%`,
        textAlign: 'right',
      }
      : {
        left: `${valuePercentage}%`,
      };
    return (h("span", { class: `scale-bar__value-label ${classes}`, style: styles, "aria-hidden": "true" }, description));
  }
  ticks(max) {
    const numberOfTicks = max - 1;
    const widthPerTick = 100 / max;
    return new Array(numberOfTicks)
      .fill(0)
      .map((_v, i) => (h("div", { class: "scale-bar__tick", style: { left: `${(i + 1) * widthPerTick}%` } })));
  }
  render() {
    var _a;
    const { classes, getValueDescription, maxLabel, minLabel } = this;
    const max = Math.max(this.max, 1);
    const value = Math.min(Math.max(0, this.currentValue || 0), max);
    const valuePercentage = (100 * value) / max;
    const valueDescription = getValueDescription(value, max);
    const labelText = (_a = document.getElementById(this.labelId)) === null || _a === void 0 ? void 0 : _a.innerText;
    const srValueDescription = labelText
      ? `${labelText} is ${valueDescription}`
      : valueDescription;
    const srLabelDescription = `0: ${minLabel}, ${max}: ${maxLabel}`;
    return (h("div", { class: `scale-bar ${classes}`, ref: (el) => (this.container = el) }, h("div", { class: "scale-bar__bar" }, h("div", { class: "scale-bar__active-area", style: { width: `${valuePercentage}%` } }), this.currentValue !== undefined &&
      this.valueLabel(valuePercentage, valueDescription), this.ticks(max), h("span", { class: "u-visually-hidden" }, srValueDescription)), (minLabel || maxLabel) && (h("div", { class: "scale-bar__range-label-container" }, h("span", { class: "scale-bar__range-label", "aria-hidden": "true" }, minLabel), h("span", { class: "scale-bar__range-label", "aria-hidden": "true" }, maxLabel), h("span", { class: "u-visually-hidden" }, srLabelDescription)))));
  }
};
ScaleBar.style = scaleBarCss;

export { ScaleBar as d4l_scale_bar };
