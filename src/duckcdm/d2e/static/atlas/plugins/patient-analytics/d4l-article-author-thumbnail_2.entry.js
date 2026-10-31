import { r as registerInstance, h, H as Host } from './index-001d5b4b.js';
import { h as href } from './index-13b9ea17.js';

const articleAuthorThumbnailCss = ".article-author-thumbnail__container{display:block}.article-author-thumbnail__link{display:block;text-decoration:none}.article-author-thumbnail.article-author-thumbnail.article-author-thumbnail{display:block}.article-author-thumbnail{width:32px;height:32px;line-height:32px;text-align:center;letter-spacing:2px;font-weight:500;font-size:0.7rem;color:var(--color-neutral)}.article-author-thumbnail img{display:block;width:32px;height:32px;box-sizing:content-box;border:3px solid #fff;background:var(--color-neutral-lighter)}.article-author-thumbnail--large{width:48px;height:48px;line-height:48px}.article-author-thumbnail--large img{width:48px;height:48px;border:0 none}";

const ArticleAuthorThumbnailComponent = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.baseUrl = '/';
    this.large = false;
  }
  get initials() {
    return this.author.name
      .split(' ')
      .map((part) => part.slice(0, 1).toUpperCase())
      .join('');
  }
  render() {
    const { pictures, uri, name } = this.author;
    return (pictures && (h("a", { class: "article-author-thumbnail__link", ...href(`${this.baseUrl}${uri}`, this.router) }, h("d4l-responsive-image", { class: "article-author-thumbnail__container", classes: `article-author-thumbnail responsive-image--portrait ${this.large ? 'article-author-thumbnail--large' : ''} ${this.classes}`, alt: this.initials, title: name, "aria-label": name, "mobile-src": this.large ? pictures.medium : pictures.small }))));
  }
};
ArticleAuthorThumbnailComponent.style = articleAuthorThumbnailCss;

const responsiveImageCss = ".responsive-image.sc-d4l-responsive-image{display:inline-block}.responsive-image.sc-d4l-responsive-image img.sc-d4l-responsive-image{display:block}.responsive-image--portrait.sc-d4l-responsive-image img.sc-d4l-responsive-image{border-radius:50%;overflow:hidden}.responsive-image--clickable.sc-d4l-responsive-image{cursor:pointer}";

const ResponsiveImage = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.classes = '';
    this.mobileSrc = '';
    this.tabletSrc = '';
    this.desktopSrc = '';
    this.widescreenSrc = '';
    this.alt = '';
    this.breakpoints = {
      mobile: 0,
      tablet: 768,
      desktop: 960,
      widescreen: 1152,
    };
  }
  get defaultSrc() {
    return (this.mobileSrc ||
      'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7');
  }
  render() {
    const { alt, classes, handleClick, defaultSrc, mobileSrc, tabletSrc, desktopSrc, widescreenSrc, } = this;
    const { mobile, tablet, desktop, widescreen } = this.breakpoints;
    return (h(Host, null, h("picture", { class: `responsive-image ${handleClick ? 'responsive-image--clickable' : ''} ${classes}`, onClick: handleClick }, widescreenSrc && (h("source", { media: `(min-width: ${widescreen}px)`, srcSet: widescreenSrc })), desktopSrc && (h("source", { media: `(min-width: ${desktop}px)`, srcSet: desktopSrc })), tabletSrc && (h("source", { media: `(min-width: ${tablet}px)`, srcSet: tabletSrc })), mobileSrc && (h("source", { media: `(min-width: ${mobile}px)`, srcSet: mobileSrc })), h("img", { loading: "lazy", src: defaultSrc, alt: alt }))));
  }
};
ResponsiveImage.style = responsiveImageCss;

export { ArticleAuthorThumbnailComponent as d4l_article_author_thumbnail, ResponsiveImage as d4l_responsive_image };
