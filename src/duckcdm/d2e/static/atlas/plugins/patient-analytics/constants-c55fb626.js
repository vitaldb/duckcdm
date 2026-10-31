const KEY_VALUES = {
  ENTER: 'Enter',
  ESC: 'Escape',
  SPACE: ' ',
  UP: 'ArrowUp',
  DOWN: 'ArrowDown',
  RIGHT: 'ArrowRight',
  LEFT: 'ArrowLeft',
  TAB: 'Tab',
  SHIFT: 'Shift',
  HOME: 'Home',
  END: 'End',
};
const KEY_EVENTS = {
  isEnter: ({ key, keyCode }) => key === KEY_VALUES.ENTER || keyCode === 13,
  isEsc: ({ key, keyCode }) => key === KEY_VALUES.ESC || keyCode === 27,
  isSpace: ({ key, keyCode }) => key === KEY_VALUES.SPACE || keyCode === 32,
  isUp: ({ key, keyCode }) => key === KEY_VALUES.UP || keyCode === 38,
  isDown: ({ key, keyCode }) => key === KEY_VALUES.DOWN || keyCode === 40,
  isRight: ({ key, keyCode }) => key === KEY_VALUES.RIGHT || keyCode === 39,
  isLeft: ({ key, keyCode }) => key === KEY_VALUES.LEFT || keyCode === 37,
  isTab: ({ key, keyCode }) => key === KEY_VALUES.TAB || keyCode === 9,
  isShift: ({ key, keyCode }) => key === KEY_VALUES.SHIFT || keyCode === 16,
  isHome: ({ key, keyCode }) => key === KEY_VALUES.HOME || keyCode === 36,
  isEnd: ({ key, keyCode }) => key === KEY_VALUES.END || keyCode === 35,
  isShiftModifier: ({ shiftKey }) => !!shiftKey,
};
const focusableElements = `a[href]:not([tabindex^="-"]):not([inert]),
   area[href]:not([tabindex^="-"]):not([inert]),
   input:not([disabled]):not([inert]),
   select:not([disabled]):not([inert]),
   textarea:not([disabled]):not([inert]),
   button:not([disabled]):not([inert]),
   iframe:not([tabindex^="-"]):not([inert]),
   audio:not([tabindex^="-"]):not([inert]),
   video:not([tabindex^="-"]):not([inert]),
   [contenteditable]:not([tabindex^="-"]):not([inert]),
   [tabindex]:not([tabindex^="-"]):not([inert])`;
const SPACES = {
  extraSmall: 'xxs',
  small: 'xs',
  normal: 's',
  medium: 'm',
  large: 'l',
  extraLarge: 'xl',
  superExtraLarge: 'xxl',
};

export { KEY_EVENTS as K, SPACES as S, focusableElements as f };
