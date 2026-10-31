import { r as registerInstance, c as createEvent, h } from './index-001d5b4b.js';
import { K as KEY_EVENTS, f as focusableElements } from './constants-c55fb626.js';

const modalCss = ".modal.sc-d4l-modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;z-index:998;width:100%;height:100%;overflow:auto;padding:16px}.modal--backdrop.sc-d4l-modal{background-color:rgba(0, 0, 0, 0.4)}.modal--open.sc-d4l-modal{display:flex;flex-flow:row nowrap;align-items:center;justify-content:flex-start}.modal__inner.sc-d4l-modal{position:relative;height:auto;min-width:310px;max-width:500px;width:40vw;margin:auto;flex:none;background-color:white;border-radius:var(--border-radius-large, var(--border-radius-m));z-index:999}.modal--backdrop.sc-d4l-modal>.modal__inner.sc-d4l-modal{box-shadow:var(--shadow-l)}.modal--corners-s.sc-d4l-modal .modal__inner.sc-d4l-modal{border-radius:var(--border-radius-xs)}.modal--corners-m.sc-d4l-modal .modal__inner.sc-d4l-modal{border-radius:var(--border-radius-s)}.modal__title.sc-d4l-modal{display:flex;flex-direction:row;justify-content:space-between;border-bottom:1px solid var(--color-neutral-lightest);padding:18px var(--space-m);align-items:center}.modal__title.sc-d4l-modal span.sc-d4l-modal{font-size:1.25em;font-weight:500}.modal__close.sc-d4l-modal{margin:0;border:none;background:transparent;cursor:pointer}.modal__content.sc-d4l-modal{padding:var(--space-m);text-align:left;overflow-x:auto}.modal__footer.sc-d4l-modal{display:flex;flex-direction:row;justify-content:center;border-top:1px solid var(--color-neutral-lightest);padding:var(--space-m);align-items:center}.modal__footer.sc-d4l-modal:empty{display:none}@media screen and (max-width: 350px){.modal.sc-d4l-modal{padding:0}}";

const Modal = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.showModal = createEvent(this, "showModal", 7);
    this.initiallyVisible = false;
    this.closeAriaLabel = 'close';
    this.closable = true;
    this.header = true;
    this.priority = 0;
    this.backdrop = false;
  }
  showModalHandler(event) {
    var _a;
    if (event.detail.id === this.modalId) {
      this.open = event.detail.show;
    }
    if (this.open) {
      this.lastFocus = document.activeElement;
      this.firstFocusableElement && this.firstFocusableElement.focus();
    }
    else {
      (_a = this.lastFocus) === null || _a === void 0 ? void 0 : _a.focus();
    }
  }
  async show() {
    this.showModal.emit({ show: true, id: this.modalId, priority: this.priority });
  }
  async hide() {
    this.showModal.emit({ show: false, id: this.modalId, priority: this.priority });
  }
  keydownHandler(event) {
    var _a, _b;
    if (!this.open) {
      return;
    }
    if (KEY_EVENTS.isEsc(event) && this.closable) {
      this.hide();
    }
    if (KEY_EVENTS.isTab(event)) {
      if (KEY_EVENTS.isShiftModifier(event)) {
        if (document.activeElement === this.firstFocusableElement) {
          (_a = this.lastFocusableElement) === null || _a === void 0 ? void 0 : _a.focus();
          event.preventDefault();
        }
      }
      else {
        if (document.activeElement === this.lastFocusableElement) {
          (_b = this.firstFocusableElement) === null || _b === void 0 ? void 0 : _b.focus();
          event.preventDefault();
        }
      }
    }
  }
  componentWillLoad() {
    this.initiallyVisible && this.show();
  }
  componentDidLoad() {
    this.open &&
      window.requestAnimationFrame(() => { var _a; return (_a = this.firstFocusableElement) === null || _a === void 0 ? void 0 : _a.focus(); });
  }
  componentDidRender() {
    var _a, _b;
    this.firstFocusableElement =
      this.modal.querySelectorAll(focusableElements)[0];
    this.focusableContent =
      this.modal.querySelectorAll(focusableElements);
    this.lastFocusableElement =
      this.focusableContent[this.focusableContent.length - 1];
    (_a = this.firstFocusableElement) === null || _a === void 0 ? void 0 : _a.focus();
    this.backdrop =
      ((_b = Array.from(document.querySelectorAll('d4l-modal .modal--open')).sort((a, b) => parseInt(a.parentElement.getAttribute('priority')) -
        parseInt(b.parentElement.getAttribute('priority')))[0]) === null || _b === void 0 ? void 0 : _b.parentElement['modalId']) === this.modalId;
  }
  render() {
    const { classes, open, modalId, labelledBy, closeAriaLabel, closable, header } = this;
    return (h("div", { ref: (el) => (this.modal = el), class: `modal ${classes || ''} ${open ? 'modal--open' : ''} ${this.backdrop ? 'modal--backdrop' : ''}`, style: { 'z-index': `${1000 + this.priority}` }, role: "dialog", id: `modal--${modalId}`, "aria-modal": "true", "aria-hidden": !(open === null || open === void 0 ? void 0 : open.toString()) || 'false', "aria-labelledby": labelledBy, onClick: (e) => {
        e.preventDefault();
        closable && this.hide();
      } }, h("div", { class: "modal__inner", onClick: (e) => e.stopPropagation() }, header && (h("div", { class: "modal__title" }, h("span", null, h("slot", { name: "modal-header" })), closable && (h("button", { type: "button", class: "modal__close", "aria-label": closeAriaLabel, title: closeAriaLabel, onClick: (e) => {
        e.preventDefault();
        this.hide();
      } }, h("d4l-icon-close", { classes: "icon--small" }))))), h("div", { class: "modal__content" }, h("slot", { name: "modal-content" })), h("div", { class: "modal__footer" }, h("slot", { name: "modal-footer" })), h("slot", null))));
  }
};
Modal.style = modalCss;

export { Modal as d4l_modal };
