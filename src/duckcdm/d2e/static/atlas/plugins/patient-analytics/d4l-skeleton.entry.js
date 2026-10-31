import { r as registerInstance, h, H as Host } from './index-001d5b4b.js';

const skeletonCss = "@keyframes translate-horizontal{100%{transform:translateX(100%)}}.skeleton{height:10em;position:relative;overflow:hidden;background-color:var(--color-neutral-lightest);border-radius:var(--border-radius-xs)}.skeleton::after{content:'';position:absolute;top:0;right:0;bottom:0;left:0;transform:translateX(-100%);background-image:linear-gradient(\n    90deg,\n    rgba(255, 255, 255, 0) 0,\n    rgba(255, 255, 255, 0.2) 20%,\n    rgba(255, 255, 255, 0.5) 60%,\n    rgba(255, 255, 255, 0)\n  );animation:translate-horizontal 1.8s infinite;z-index:9999}";

const Skeleton = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.loading = true;
  }
  render() {
    const { classes, loading, width, height, otherStyle } = this;
    return (h(Host, null, loading ? (h("div", { class: `skeleton ${classes ? classes : ''}`, style: { width, height, ...otherStyle } })) : (h("slot", null))));
  }
};
Skeleton.style = skeletonCss;

export { Skeleton as d4l_skeleton };
