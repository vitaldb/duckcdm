import { r as registerInstance, h } from './index-001d5b4b.js';
import { S as SPACES } from './constants-c55fb626.js';

const dividerCss = ".divider{background-color:var(--color-neutral-lightest);height:1px}.divider-container{display:flex;align-items:center}.divider-container .divider{flex:1}.divider-container .divider-text{padding:0 var(--space-s)}.u-padding-horizontal--small .divider,.u-padding--small .divider{margin-left:calc(-1 * var(--padding-small));margin-right:calc(-1 * var(--padding-small))}.u-padding-left--small .divider{margin-left:calc(-1 * var(--padding-small))}.u-padding-right--small .divider{margin-right:calc(-1 * var(--padding-small))}.u-padding-horizontal--normal .divider,.u-padding--normal .divider{margin-left:calc(-1 * var(--padding-normal));margin-right:calc(-1 * var(--padding-normal))}.u-padding-left--normal .divider{margin-left:calc(-1 * var(--padding-normal))}.u-padding-right--normal .divider{margin-right:calc(-1 * var(--padding-normal))}.u-padding-horizontal--medium .divider,.u-padding--medium .divider{margin-left:calc(-1 * var(--padding-medium));margin-right:calc(-1 * var(--padding-medium))}.u-padding-left--medium .divider{margin-left:calc(-1 * var(--padding-medium))}.u-padding-right--medium .divider{margin-right:calc(-1 * var(--padding-medium))}";

const Divider = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
  }
  render() {
    const margins = [
      `u-margin-bottom--${SPACES[this.marginBottom] || 's'}`,
      `u-margin-top--${SPACES[this.marginTop] || 's'}`,
    ];
    if (this.text) {
      return (h("div", { class: `divider-container ${margins.join(' ')}` }, h("div", { class: "divider" }), h("span", { class: "divider-text" }, this.text), h("div", { class: "divider" })));
    }
    else {
      return h("div", { class: `divider ${margins.join(' ')}` });
    }
  }
};
Divider.style = dividerCss;

export { Divider as d4l_divider };
