import { r as registerInstance, h } from './index-001d5b4b.js';

const linearProgressCss = ".linear-progress.sc-d4l-linear-progress{--progress-percentage:0;width:auto;height:5px;background-color:var(--color-neutral-lightest);position:relative;overflow:hidden}.linear-progress.sc-d4l-linear-progress::after{content:'';position:absolute;top:0;left:0;right:0;height:5px;background-color:var(--color-primary);transition:transform 0.2s linear;transform:translateX(var(--progress-percentage))}";

const LinearProgress = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.value = 0;
  }
  componentDidLoad() {
    this.linearProgressElement.style.setProperty('--progress-percentage', `${(100 - this.value) * -1}%`);
  }
  componentDidUpdate() {
    this.linearProgressElement.style.setProperty('--progress-percentage', `${(100 - this.value) * -1}%`);
  }
  render() {
    const { classes, value, label } = this;
    return (h("div", { role: "progressbar", "aria-valuenow": value, "aria-label": label, class: `linear-progress ${classes}`, ref: (el) => (this.linearProgressElement = el) }));
  }
};
LinearProgress.style = linearProgressCss;

export { LinearProgress as d4l_linear_progress };
