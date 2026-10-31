import { r as registerInstance, h, H as Host } from './index-001d5b4b.js';

const iconCss = ".icon{display:block;width:48px;height:48px;color:var(--color-primary);fill:currentColor}.icon__fill--primary-color{fill:var(--color-primary)}.icon__fill--secondary-color{fill:var(--color-secondary)}.icon__fill--none{fill:none}.icon--small{width:24px;height:24px}.icon--flag{width:28px;height:20px}.icon--medium{width:36px;height:36px}.icon--extra-small{width:18px;height:18px}.icon--extra-smaller{width:16px;height:16px}.icon--size-auto{width:auto;height:auto}.icon--current-color{fill:currentColor;color:currentColor}.icon--circle{border-radius:50%;padding:calc(var(--space-xs) + 2px);overflow:visible}.icon--bg-white{background-color:#fff}.icon--bg-primary{background-color:var(--color-primary);color:#fff}.icon--bg-tertiary-light{background-color:var(--color-tertiary-light)}.icon--bg-tertiary-lime{background-color:var(--color-support-green)}.icon--bg-tertiary-yellow{background-color:var(--color-support-yellow)}.icon--bg-neutral-lightest{background-color:var(--color-neutral-lightest)}.icon--bg-tertiary-blue{background-color:var(--color-support-blue)}.icon--rotate-180{transform:rotate(180deg)}.icon--animated-transform{transition:transform 0.2s ease}.icon--margin-horizontal-xss{margin-left:var(--space-xxs);margin-right:var(--space-xxs)}.icon--margin-right-xss{margin-right:var(--space-xxs)}.icon--button{color:var(--color-text-button-primary-default)}.button--alarm .icon--button{color:var(--color-text-button-alarm-default)}";

const IconI18n = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
  }
  render() {
    return (h(Host, { "aria-hidden": "true", role: "presentation" }, h("svg", { class: `icon ${this.classes}`, viewBox: "0 0 20 20", xmlns: "http://www.w3.org/2000/svg", focusable: this.focusable }, h("path", { d: "M10 0c5.523 0 10 4.477 10 10s-4.477 10-10 10S0 15.523 0 10 4.477 0 10 0zM5.503 10.91H1.868c.376 3.397 2.831 6.166 6.064 7.008-1.382-2.08-2.222-4.485-2.43-7.008zm12.629 0H14.5c-.204 2.511-1.045 4.922-2.432 7.008 3.233-.842 5.688-3.611 6.064-7.008zm-5.455 0H7.325c.229 2.465 1.156 4.813 2.675 6.77 1.524-1.964 2.454-4.32 2.677-6.77zM7.932 2.082l-.107.028c-3.18.875-5.585 3.621-5.957 6.98H5.5c.204-2.511 1.045-4.922 2.432-7.008zM10 2.318C8.476 4.284 7.546 6.64 7.323 9.09h5.352C12.446 6.625 11.519 4.277 10 2.318zm2.068-.236l.014.022c1.374 2.074 2.208 4.471 2.415 6.986h3.635c-.376-3.397-2.831-6.166-6.064-7.008z", transform: "translate(-58 -197) translate(50 187) translate(8 10)" }))));
  }
};
IconI18n.style = iconCss;

export { IconI18n as d4l_icon_i18n };
