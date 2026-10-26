import "@tanstack/react-table";

declare module "@tanstack/react-table" {
  interface ColumnMeta<TData extends RowData, TValue> {
    /** Filter-only column: never rendered, but can hold a column filter. */
    hidden?: boolean;
  }
}
