import { r as registerInstance, h } from './index-001d5b4b.js';
import { h as href } from './index-13b9ea17.js';

const articleCss = ".article{line-height:1.43;color:var(--color-primary)}.article__cover{display:block;width:100%}.article__cover--author{width:80px;height:80px;border-radius:50%;margin:var(--space-s) auto 0;overflow:hidden;background:var(--color-neutral-lighter)}.article__tags{display:flex;flex-flow:row;margin:var(--space-xs) 0 var(--space-m)}.article__tags a{text-decoration:none;margin:0 var(--space-xs) 0 0;display:block}.article__content{padding:var(--space-s)}.article__date{font-size:var(--font-size-mobile-xs);color:var(--color-neutral)}.article__byline{display:flex;flex-flow:row nowrap;margin:var(--space-xs) 0 var(--space-m)}.article__author-thumbnails{display:flex;flex-flow:row nowrap;flex:none}.article__author-thumbnail{display:block;position:relative;flex:none;margin:-3px}.article__author-thumbnail+.article__author-thumbnail{margin-left:-7px}.article__author-links{line-height:32px;margin-left:0.8rem;font-size:var(--font-size-mobile-s);color:var(--color-neutral)}.article__author-links a{color:var(--color-primary);font-weight:500}.article__title{font-weight:500;margin:var(--space-xs) 0 var(--space-m);font-size:var(--font-size-mobile-xl)}.article__title a{text-decoration:none;color:var(--color-primary)}.article__title a:hover,.article__title a:focus{text-decoration:underline}.article__title--author{text-align:center;margin:0 0 var(--space-m)}.article__bio{padding:var(--space-s) var(--space-s) var(--space-l)}.article__bio+.article__bio{padding-top:0}.article__bio-headline{text-align:center;padding:var(--space-m) var(--space-s) var(--space-s);color:var(--color-neutral)}.article__divider{margin:0;padding:0;border:0 none;border-top:1px solid var(--color-neutral-lighter)}@media screen and (min-width: 768px){.article__cover--author{margin:var(--space-xl) auto calc(var(--space-m) - var(--space-l))}.article__content{padding:var(--space-l) var(--space-xxl)}.article__date{font-size:var(--font-size-desktop-xs)}.article__title{font-size:var(--font-size-desktop-xl)}.article__bio{padding:var(--space-l)}.article__bio-headline{padding:var(--space-m);padding-bottom:0}.article__author-thumbnail+.article__author-thumbnail{margin-left:-11px}}";

const ArticleComponent = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.layout = 'full';
    this.context = 'standalone';
    this.showRating = true;
    this.showBio = false;
    this.baseUrl = '/';
    this.renderCover = (article) => {
      var _a;
      const { isPreviewLayout, isAuthorLayout } = this;
      return (h("img", { class: `article__cover ${isAuthorLayout ? 'article__cover--author' : ''}`, loading: "lazy", src: !isPreviewLayout ? article.cover.full : article.cover.preview, alt: (_a = article.cover.alt) !== null && _a !== void 0 ? _a : article.title }));
    };
  }
  get formattedDate() {
    var _a, _b, _c;
    const date = this.article.publicationDate;
    if ((_a = this.article.flags) === null || _a === void 0 ? void 0 : _a.includes('CUSTOM_DATE')) {
      return date;
    }
    return (_c = (_b = this.dateFormatter) === null || _b === void 0 ? void 0 : _b.call(this, date)) !== null && _c !== void 0 ? _c : date;
  }
  get isFullLayout() {
    return this.layout === 'full';
  }
  get isPreviewLayout() {
    return this.layout === 'preview';
  }
  get isAuthorLayout() {
    return this.layout === 'author';
  }
  get isEmbeddedContext() {
    return this.context === 'embedded';
  }
  componentDidRender() {
    var _a;
    (_a = this.dateElRef) === null || _a === void 0 ? void 0 : _a.querySelectorAll('[data-corona-statistic]').forEach((statEl) => {
      var _a, _b;
      const { coronaStatistic: src } = statEl.dataset;
      statEl.innerHTML = String((_b = (_a = this.coronaStats) === null || _a === void 0 ? void 0 : _a[src]) !== null && _b !== void 0 ? _b : '…');
    });
  }
  render() {
    var _a, _b, _c, _d;
    const { article, classes, isFullLayout, isPreviewLayout, isAuthorLayout, isEmbeddedContext, renderCover, baseUrl, router, } = this;
    return (h("article", { class: `article ${classes}` }, h("slot", { name: "article-header" }, !isPreviewLayout ? (renderCover(article)) : (h("a", { ...href(`${baseUrl}${article.uri}`, router) }, renderCover(article)))), h("div", { class: "article__content" }, h("slot", { name: "article-content" }, h("slot", { name: "article-meta" }, !isAuthorLayout && !!this.article.publicationDate && (h("div", { class: "article__date", ref: (el) => (this.dateElRef = el), innerHTML: this.formattedDate }))), h("h2", { class: `article__title ${isAuthorLayout ? 'article__title--author' : ''}` }, !isPreviewLayout ? (article.title) : (h("a", { ...href(`${baseUrl}${article.uri}`, router) }, article.title))), !isEmbeddedContext && ((_a = article.topics) === null || _a === void 0 ? void 0 : _a.length) > 0 && (h("div", { class: "article__tags" }, article.topics.slice(0, 2).map((topic) => (h("a", { key: topic.uid, ...href(`${baseUrl}articles?topics=${topic.uid}`, router) }, h("d4l-tag", { class: "article__tag", text: topic.title })))))), isFullLayout && !!((_b = article.authors) === null || _b === void 0 ? void 0 : _b.length) && (h("div", { class: "article__byline" }, h("div", { class: "article__author-thumbnails" }, article.authors.map((author, index) => (h("d4l-article-author-thumbnail", { class: "article__author-thumbnail", author: author, key: author.uid, baseUrl: baseUrl, router: router, style: { zIndex: String(article.authors.length - index) } })))), h("div", { class: "article__author-links" }, h("slot", { name: "article-author-links" }, article.authors.map(({ name }) => name).join(', '), ' ')))), h("slot", { name: "article-copy" }, !isPreviewLayout
      ? (_c = article.contentSections) === null || _c === void 0 ? void 0 : _c.map((section) => (h("d4l-article-content-section", { section: section, key: section.id, coronaStats: this.coronaStats, isEmbeddedContext: isEmbeddedContext })))
      : !!article.excerpt && (h("d4l-article-content-section", { section: {
          id: article.uid,
          type: 'paragraph',
          content: article.excerpt,
        }, key: article.uid, isEmbeddedContext: isEmbeddedContext }))))), this.showRating && (h("slot", { name: "article-rating" }, h("hr", { class: "article__divider" }), h("d4l-article-rating", { rating: this.rating, headline: this.ratingHeadline, "label-up": this.ratingLabelUp, "label-down": this.ratingLabelDown }))), this.showBio && !!((_d = article.authors) === null || _d === void 0 ? void 0 : _d.length) && (h("slot", { name: "article-bio" }, h("hr", { class: "article__divider" }), this.bioHeadline && (h("div", { class: "article__bio-headline" }, this.bioHeadline)), article.authors.map((author) => (h("div", { class: "article__bio" }, h("d4l-article-author-bio", { author: author, key: author.uid, baseUrl: baseUrl, labelMore: this.bioLabelMore, router: router }))))))));
  }
};
ArticleComponent.style = articleCss;

export { ArticleComponent as d4l_article };
