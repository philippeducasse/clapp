import React from 'react'
import { Search } from "lucide-react";
import CreateButton from "../buttons/CreateButton";
interface DataTableHeaderProps{
    globalFilter: string,
    setGlobalFilter: (value:string) => void
    entityName: string,
}

const DataTableHeader = ({globalFilter, setGlobalFilter, entityName}: DataTableHeaderProps) => {
  return (
    <div className="flex items-center justify-between">
        <div className="flex max-w-sm h-10 items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2 dark:bg-background dark:border-gray-700">
          <Search className="h-[16px] w-[16px]" />
          <input
            placeholder="Search"
            value={globalFilter}
            onChange={(event) => setGlobalFilter(event.target.value)}
            type="search"
            className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:text-foreground"
          />
        </div>

        <CreateButton label={`Create new ${entityName}`} href={`${entityName}s/create`} />
      </div>
  )
}

export default DataTableHeader