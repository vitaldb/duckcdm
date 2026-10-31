import { r as registerInstance, h, c as createEvent, H as Host } from './index-001d5b4b.js';
import { h as href } from './index-13b9ea17.js';

const articleAuthorBioCss = ".article-author-bio{text-align:left;display:block;font-size:var(--font-size-desktop-s);line-height:1.5;color:var(--color-primary)}.article-author-bio__picture{width:48px;margin:0 auto var(--space-xs)}.article-author-bio__name{text-align:center;font-weight:500;font-size:inherit;margin:0 0 var(--space-xs)}.article-author-bio a{color:inherit}@media screen and (min-width: 768px){.article-author-bio{display:flex;flex-flow:row wrap;align-items:flex-start}.article-author-bio__picture{flex:none;margin:0 var(--space-s) 0 0}.article-author-bio__name{text-align:left}.article-author-bio__text{flex:1}}";

const ArticleAuthorBioComponent = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.baseUrl = '/';
  }
  render() {
    const { router } = this;
    return (h("div", { class: "article-author-bio" }, h("div", { class: "article-author-bio__picture" }, h("d4l-article-author-thumbnail", { author: this.author, baseUrl: this.baseUrl, router: router, large: true })), h("div", { class: "article-author-bio__text" }, h("h4", { class: "article-author-bio__name" }, this.author.name), h("div", { innerHTML: this.author.excerpt }), !!this.labelMore && (h("a", { ...href(`${this.baseUrl}${this.author.uri}`, router) }, this.labelMore)))));
  }
};
ArticleAuthorBioComponent.style = articleAuthorBioCss;

const articleContentSectionCss = ".article__content-section{display:block;font-size:var(--font-size-mobile-s);color:var(--color-primary)}.article--embedded .article__content-section{line-height:24px}.article__content-section--headline{margin:var(--space-l) 0 var(--space-xs);font-weight:500}.article--embedded .article__content-section--headline{margin:var(--space-l) 0 calc(var(--space-m) / 2)}.article__content-section--h3{font-size:var(--font-size-mobile-l)}.article__content-section--h4{font-size:var(--font-size-mobile-m)}.article__content-section--h5{font-size:var(--font-size-mobile-s)}.article--embedded .article__content-section--h5{margin-top:var(--space-m)}.article__content-section--paragraph,.article__content-section--list{margin:var(--space-xs) 0 var(--space-s)}.article--embedded .article__content-section--paragraph,.article--embedded .article__content-section--list{margin:var(--space-xs) 0 var(--space-m)}.article__content-section--paragraph strong{font-weight:500}.article__content-section--paragraph a{color:inherit;font-weight:500}.article__content-section--list{padding:0 0 0 1em;list-style-position:outside}.article__content-section--blockquote{margin:var(--space-s) 0;padding:0 var(--space-s);border-left:3px solid var(--color-primary-light);font-style:italic}.article--embedded .article__content-section--blockquote{margin:var(--space-m) 0}.article__content-section--image{margin:var(--space-m) 0;padding:0}.article__content-section--image img{display:block;width:100%}.article__content-section--image figcaption{display:block;text-align:center;font-size:var(--font-size-mobile-xs);color:var(--color-neutral);margin:var(--space-xs) 0 0}.article--embedded .article__content-section--image figcaption{text-align:left}.article__content-section--corona{padding:var(--space-m) var(--space-l);margin:var(--space-s) 0;text-align:center;border-radius:var(--border-radius-m)}.article__content-section--corona h3{font-weight:500;margin:0;font-size:calc(var(--font-size-desktop-xl) + 3px)}.article__content-section--corona p{margin:0 0 var(--space-xs);font-size:var(--font-size-desktop-xl)}.article__content-section--corona-green{background-color:var(--color-support-green)}.article__content-section--corona-red{background-color:var(--color-secondary-light)}.article__content-section--corona-blue{background-color:var(--color-primary-light)}.article__content-section--corona-blue>*{color:#fff}.article__content-section--unknown{margin:var(--space-m) 0}@media screen and (min-width: 768px){.article__content-section{font-size:var(--font-size-desktop-s)}.article__content-section--h3{font-size:var(--font-size-desktop-l)}.article__content-section--h4{font-size:var(--font-size-desktop-m)}.article__content-section--h5{font-size:var(--font-size-desktop-s)}.article__content-section--image figcaption{font-size:var(--font-size-desktop-xs)}}";

var __classPrivateFieldGet = (undefined && undefined.__classPrivateFieldGet) || function (receiver, state, kind, f) {
  if (kind === "a" && !f)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var __classPrivateFieldSet = (undefined && undefined.__classPrivateFieldSet) || function (receiver, state, value, kind, f) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return (kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value)), value;
};
var _ArticleContentSectionComponent_paragraphElRef;
const ArticleContentSectionComponent = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    _ArticleContentSectionComponent_paragraphElRef.set(this, void 0);
    this.classes = '';
    this.isEmbeddedContext = false;
    this.getClasses = (...modifiers) => `article__content-section ${modifiers
      .map((modifier) => `article__content-section--${modifier}`)
      .join(' ')} ${this.classes}`;
  }
  componentDidLoad() {
    var _a;
    (_a = __classPrivateFieldGet(this, _ArticleContentSectionComponent_paragraphElRef, "f")) === null || _a === void 0 ? void 0 : _a.querySelectorAll('a').forEach((linkEl) => {
      var _a;
      if (((_a = linkEl.href) === null || _a === void 0 ? void 0 : _a.indexOf(document.location.origin)) === 0) {
        return;
      }
      linkEl.setAttribute('rel', 'noopener noreferrer');
      linkEl.setAttribute('target', this.isEmbeddedContext ? '_self' : '_blank');
    });
  }
  componentDidRender() {
    var _a;
    (_a = __classPrivateFieldGet(this, _ArticleContentSectionComponent_paragraphElRef, "f")) === null || _a === void 0 ? void 0 : _a.querySelectorAll('[data-corona-statistic]').forEach((statEl) => {
      var _a, _b;
      const { coronaStatistic: src } = statEl.dataset;
      statEl.innerHTML = String((_b = (_a = this.coronaStats) === null || _a === void 0 ? void 0 : _a[src]) !== null && _b !== void 0 ? _b : '…');
    });
  }
  render() {
    var _a;
    const { getClasses, coronaStats } = this;
    const { type, content, attrs } = this.section;
    let TagName;
    switch (type) {
      case 'h1':
      case 'h2':
      case 'h3':
        const prio = type.slice(-1);
        TagName = type.replace(prio, String(parseInt(prio, 10) + 2));
        return h(TagName, { class: getClasses('headline', TagName) }, content);
      case 'paragraph':
      case 'kirbytext':
        return (h("div", { ref: (el) => (__classPrivateFieldSet(this, _ArticleContentSectionComponent_paragraphElRef, el, "f")), class: getClasses('paragraph'), innerHTML: content }));
      case 'ul':
      case 'ol':
        TagName = type;
        return (h(TagName, { class: getClasses('list') }, [].concat(content).map((item) => (h("li", null, item)))));
      case 'blockquote':
        return h("blockquote", { class: getClasses('blockquote') }, content);
      case 'image':
        return (h("figure", { class: getClasses('image') }, h("img", { loading: "lazy", src: attrs.src, alt: attrs.alt }), !!attrs.caption && h("figcaption", null, attrs.caption)));
      case 'corona':
        return (h("div", { class: getClasses('corona', `corona-${attrs.meta.theme}`) }, h("h3", null, (_a = coronaStats === null || coronaStats === void 0 ? void 0 : coronaStats[attrs.src]) !== null && _a !== void 0 ? _a : '…'), h("p", null, content)));
    }
    // TODO implement types code and video
    const errorText = `Unsupported content section type: ${this.section.type}`;
    window.requestAnimationFrame(() => {
      throw new Error(errorText);
    });
    return (h("d4l-notification-bar", { class: getClasses('unknown'), classes: "notification-bar--slim notification-bar--bgcolor-red notification-bar--color-white", headline: "Error", text: errorText }));
  }
};
_ArticleContentSectionComponent_paragraphElRef = new WeakMap();
ArticleContentSectionComponent.style = articleContentSectionCss;

const articleRatingCss = ".article__rating.sc-d4l-article-rating{text-align:center;padding:var(--space-m);color:var(--color-primary)}.article__rating-headline.sc-d4l-article-rating{color:var(--color-neutral)}.article__rating-headline.sc-d4l-article-rating:empty{display:none}.article__rating-container.sc-d4l-article-rating{display:flex;flex-flow:row nowrap;align-items:center;justify-content:center}.article__rating-trigger.sc-d4l-article-rating{display:block;position:relative;cursor:pointer;background:transparent;border:0 none;margin:var(--space-xs);padding:var(--space-s);color:currentColor}.article__rating--initial.sc-d4l-article-rating .article__rating-label.sc-d4l-article-rating{color:var(--color-neutral)}.article__rating--down.sc-d4l-article-rating .article__rating-trigger--up.sc-d4l-article-rating,.article__rating--up.sc-d4l-article-rating .article__rating-trigger--down.sc-d4l-article-rating{color:var(--color-neutral-lighter)}.article__rating--down.sc-d4l-article-rating .article__rating-trigger--down.sc-d4l-article-rating{color:var(--color-secondary)}.article__rating-label.sc-d4l-article-rating{position:absolute;left:0;width:100%;text-align:center;font-size:10px;bottom:calc(var(--space-xs) * (-1));pointer-events:none}";

const ArticleRatingComponent = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.articleRated = createEvent(this, "articleRated", 7);
    this.classes = '';
  }
  articleRatedHandler(up) {
    this.articleRated.emit(up);
  }
  get ratingClassModifier() {
    const { rating } = this;
    if (typeof rating !== 'boolean') {
      return 'initial';
    }
    return rating ? 'up' : 'down';
  }
  render() {
    const { headline, labelUp, labelDown } = this;
    return (h("div", { class: `article__rating article__rating--${this.ratingClassModifier} ${this.classes}` }, headline && h("div", { class: "article__rating-headline" }, headline), h("div", { class: "article__rating-container" }, h("button", { class: "article__rating-trigger article__rating-trigger--up", type: "button", onClick: () => this.articleRatedHandler(true) }, h("d4l-icon-like", { classes: "icon--current-color" }), labelUp && h("span", { class: "article__rating-label" }, labelUp)), h("button", { class: "article__rating-trigger article__rating-trigger--down", type: "button", onClick: () => this.articleRatedHandler(false) }, h("d4l-icon-dislike", { classes: "icon--current-color" }), labelDown && h("span", { class: "article__rating-label" }, labelDown)))));
  }
};
ArticleRatingComponent.style = articleRatingCss;

const tagCss = ".tag.sc-d4l-tag{box-sizing:border-box;border:none;border-radius:4px;padding:5px 10px;margin:0;background:var(--color-neutral-transparent);height:28px;font-size:12px;font-weight:normal;font-stretch:normal;font-style:normal;line-height:12px;letter-spacing:normal;text-align:center;color:var(--color-neutral);text-decoration:none;display:block;white-space:nowrap;transition:background 0.15s ease;cursor:pointer;outline:none}.tag.tag--active.sc-d4l-tag,.tag.sc-d4l-tag:not(:disabled):focus,.tag.sc-d4l-tag:not(:disabled):hover{color:var(--color-primary);background-color:var(--color-primary-extra-lightest)}.tag.sc-d4l-tag:disabled{cursor:not-allowed}";

const Tag = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    /** The text that is displayed */
    this.text = '';
    /** A string containing additional classes that should be added to the component */
    this.classes = '';
    /** Flag indicating if the tag is disabled or not  */
    this.disabled = false;
  }
  render() {
    const { text, classes, disabled, handleClick } = this;
    return (h(Host, null, h("button", { class: `tag ${classes}`, disabled: disabled, onClick: handleClick }, text)));
  }
};
Tag.style = tagCss;

export { ArticleAuthorBioComponent as d4l_article_author_bio, ArticleContentSectionComponent as d4l_article_content_section, ArticleRatingComponent as d4l_article_rating, Tag as d4l_tag };
