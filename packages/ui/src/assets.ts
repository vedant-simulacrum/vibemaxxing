export const assetRegistry = {
  brand: {
    marks: {
      primary: "/brand-assets/brand/source/mark-primary.svg",
      indigo: "/brand-assets/brand/source/mark-indigo.svg",
      oneColor: "/brand-assets/brand/source/mark-one-color.svg",
      light: "/brand-assets/brand/source/mark-light.svg",
      maskable: "/brand-assets/brand/source/mark-maskable.svg",
    },
    wordmarks: {
      noRule: "/brand-assets/brand/source/wordmark-no-rule.svg",
      primary: "/brand-assets/brand/source/wordmark-primary.svg",
      indigo: "/brand-assets/brand/source/wordmark-indigo.svg",
      monochrome: "/brand-assets/brand/source/wordmark-monochrome.svg",
      reverse: "/brand-assets/brand/source/wordmark-reverse.svg",
    },
    favicon: "/brand-assets/brand/source/favicon.svg",
    appIcon: "/brand-assets/brand/exports/app-icons/app-icon-512.png",
    socialCard: "/brand-assets/brand/exports/social/social-card-1200x630.png",
    wordmark: "/brand-assets/brand/source/wordmark-no-rule.svg",
  },
  fixtures: {
    currentUser: "/brand-assets/ui/fixtures/vedant-avatar.png",
    leaderboardAvatarSprite: "/brand-assets/ui/fixtures/leaderboard-avatars.png",
    storyboardAvatar: (id: number) => `/brand-assets/ui/fixtures/storyboard-avatars/${id}.svg`,
  },
} as const;
