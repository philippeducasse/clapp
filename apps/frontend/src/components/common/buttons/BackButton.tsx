import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";

interface BackButtonProps {
  href: string;
  label?: string;
}

const BackButton = ({ label, href }: BackButtonProps) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(href);
  };

  return (
    <Button size="sm" variant="outline" onClick={handleClick} type="button">
      {label ?? "Go back"}
    </Button>
  );
};

export default BackButton;
