export const assetRegistry = {
  brand: {
    wordmark: "/brand-assets/brand/source/wordmark-no-rule.svg",
  },
  fixtures: {
    currentUser: "/brand-assets/ui/fixtures/vedant-avatar.png",
    storyboardAvatar: (id: number) => `/brand-assets/ui/fixtures/storyboard-avatars/${id}.svg`,
  },
} as const;
