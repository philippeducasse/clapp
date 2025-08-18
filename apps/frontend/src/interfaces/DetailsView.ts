import { UrlObject } from "url";

export interface SectionCellProps {
  type?: SectionCellType;
  title: string;
  value?: SectionCellValueType;
  isLoading?: boolean;
  element?: React.ReactNode;
  linkTo?: UrlObject | string;
  className?: string;
  disabled?: boolean;
  valueClassName?: string;
  id?: string;
}

export type SectionCellValueType = string | number | boolean | number[] | string[] | undefined | Date;

export const enum SectionCellType {
  Text = "text",
  Element = "element",
  Badge = "badge",
  List = "list",
  Link = "link",
  Image = "img",
  Bool = "bool",
  HTML = "html",
  Log = "log",
  Video = "video",
}
