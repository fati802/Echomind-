import Image from "next/image";

export default function Logo({ height = 40 }) {
  return (
    <Image
      src="/logo.png"
      alt="EchoMind"
      width={height * 3}
      height={height}
      priority
      style={{ height: `${height}px`, width: "auto" }}
    />
  );
}
