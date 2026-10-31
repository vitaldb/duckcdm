import { r as registerInstance, h, H as Host } from './index-001d5b4b.js';

const sliderCss = "d4l-slider{color:var(--color-primary);width:100%;display:flex;justify-content:center;margin:10px 0;padding:50px 0;--slider-width:270px}.slider{width:var(--slider-width);overflow:hidden;text-align:center}.slider--text-align-left{text-align:left}.slider__container{--n-slides:1;display:flex;flex-wrap:nowrap;list-style:none;padding:0;margin:0;flex:0 0 100%;width:calc(var(--slider-width) * var(--n-slides));transform:translateX(calc(var(--current-slide) * (var(--slider-width) * -1)));transition:transform 0.2s ease-in-out}.slider__slide{display:flex;flex-direction:column;align-items:center;width:var(--slider-width);padding:0 20px;user-select:none}.slider__slide h4{margin:var(--space-s) 0;font-weight:500;width:100%}.slider__slide p{font-size:var(--font-size-desktop-s);margin-top:var(--space-s) 0 var(--space-xl)}.slide__header-content{width:100%}.slide__image{max-height:48px}.slider__controls{padding:0 20px;display:flex;justify-content:center}.slider__controls.slider__controls--with-button{justify-content:space-between}.slider__controls button{cursor:pointer}.slider__controls .slider__button-dot{padding:10px;margin:5px;position:relative;border:0;background:none}.slider__controls .slider__button-dot:before{content:'';position:absolute;width:8px;height:8px;background-color:var(--color-primary-lighter);border-radius:50%;left:50%;top:50%;transform:translate(-50%, -50%)}.slider__controls .slider__button-dot.is-active:before{background-color:var(--color-primary)}.slider__controls .slider__button-next{border:none;background:none;display:flex;align-items:center;color:var(--color-primary)}";

const Slider = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.ariaLabel = 'slider';
    this.slides = [];
    this.nextButtonTitle = undefined;
    this.positionX0 = null;
    this.numberOfSlides = 0;
    this.currentActiveSlide = 0;
    this.containerWidth = 270;
  }
  unifyTouchEvents(event) {
    return event.changedTouches ? event.changedTouches[0] : event;
  }
  navigateToSlide(slideIndex) {
    this.sliderContainer.style.setProperty('--current-slide', slideIndex);
    this.currentActiveSlide = slideIndex;
  }
  swipeStart(event) {
    this.positionX0 = this.unifyTouchEvents(event).clientX;
  }
  swipeMove(event) {
    if (this.positionX0 || this.positionX0 === 0) {
      let deltaX = this.unifyTouchEvents(event).clientX - this.positionX0;
      let deltaXSign = Math.sign(deltaX);
      if ((this.currentActiveSlide > 0 || deltaXSign < 0) &&
        (this.currentActiveSlide < this.numberOfSlides - 1 || deltaXSign > 0))
        this.sliderContainer.style.setProperty('--current-slide', (this.currentActiveSlide -= deltaXSign).toString());
      this.positionX0 = null;
    }
  }
  componentWillLoad() {
    this.numberOfSlides = this.slides.length;
  }
  componentDidLoad() {
    this.sliderContainer.style.setProperty('--n-slides', this.numberOfSlides.toString());
    this.containerWidth = this.sliderContainer.parentElement.offsetWidth;
  }
  render() {
    const { classes, ariaLabel, slides, currentActiveSlide, nextButtonTitle } = this;
    return (h(Host, { role: "region", "aria-label": ariaLabel, onTouchStart: (event) => this.swipeStart(event), onTouchEnd: (event) => this.swipeMove(event), onMouseDown: (event) => this.swipeStart(event), onMouseUp: (event) => this.swipeMove(event) }, h("div", { class: `slider ${classes}` }, h("ul", { class: "slider__container", ref: (el) => (this.sliderContainer = el) }, !!slides.length &&
      slides.map((slide) => (h("li", { class: "slider__slide" }, slide.headerContent && (h("div", { class: "slide__header-content", innerHTML: slide.headerContent })), slide.icon && h("d4l-icon", { "icon-name": slide.icon }), slide.imageUrl && (h("img", { class: "slide__image", src: slide.imageUrl })), h("h4", null, slide.title), slide.text && h("p", null, slide.text), slide.ctaLink && (h("a", { href: slide.ctaLink, target: "_blank", rel: "noopener noreferrer" }, h("d4l-button", { "is-route-link": true, class: "slide__button", text: slide.ctaText, onClick: slide.ctaEventHandler }))))))), h("div", { class: `slider__controls ${nextButtonTitle ? 'slider__controls--with-button' : ''}` }, h("span", null, slides.map((slide, index) => (h("button", { class: `slider__button-dot ${index === currentActiveSlide ? 'is-active' : ''}`, "aria-label": `Slide ${index + 1} — ${slide.label}`, title: slide.label, onClick: () => this.navigateToSlide(index) })))), nextButtonTitle && currentActiveSlide + 1 < slides.length && (h("button", { class: "slider__button-next", "aria-label": `Slide ${currentActiveSlide + 1} — ${slides[currentActiveSlide + 1].label}`, onClick: () => this.navigateToSlide(currentActiveSlide + 1) }, nextButtonTitle, ' ', h("d4l-icon-arrow-forward-ios", { classes: "icon--extra-small" })))))));
  }
};
Slider.style = sliderCss;

export { Slider as d4l_slider };
