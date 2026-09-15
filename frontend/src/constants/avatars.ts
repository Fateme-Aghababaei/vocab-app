export const AVATARS = [
  { id: "Nilo", label: "The Wise Alien — Nilo" },
  { id: "Mobi", label: "The Friendly Robot — Mobi" },
  { id: "Lumi", label: "The Stargazer Spirit — Lumi" },
  { id: "Rico", label: "The Comet Trickster — Rico" },
  { id: "Selu", label: "The Moon Guardian — Selu" },
  { id: "Orbi", label: "The Planet Keeper — Orbi" },
  { id: "Veya", label: "The Cosmic Wanderer — Veya" },
  { id: "Soli", label: "The Star Forger — Soli" },
] as const;

export type AvatarId = (typeof AVATARS)[number]["id"];

export function avatarImage(avatar: AvatarId) {
  return `/avatars/${avatar}.png`;
}
