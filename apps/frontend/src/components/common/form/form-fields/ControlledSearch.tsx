import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { ControllerRenderProps } from "react-hook-form";
import { organisationApiService, OrganisationSearchResponse } from "@/api/organisationApiService";
// import { Spinner } from "@/components/ui/spinner";
import _ from "lodash";
interface ControlledTextProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

const ControlledSearch = ({ field }: ControlledTextProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<OrganisationSearchResponse[]>([]);
  const [isLoading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isSelected, setIsSelected] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const searchOrganisations = async () => {
      if (searchQuery.length < 2) {
        setSearchResults([]);
        return;
      }
      setLoading(true);
      try {
        const searchResponse = await organisationApiService.search(searchQuery);
        setSearchResults(searchResponse);
      } catch (error) {
        console.error("Search failed:", error);
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    };
    const timeoutId = setTimeout(() => {
      searchOrganisations();
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    field.onChange(value);
    setIsSelected(false);
  };
  const handleSelectOrganisation = (org: OrganisationSearchResponse) => {
    field.onChange(org.id);
    setSearchQuery(`${_.capitalize(org.type)}: ${org.name}`);
    setShowDropdown(false);
    setSearchResults([]);
    setIsSelected(true);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <Input
        {...field}
        value={searchQuery}
        onChange={handleChange}
        placeholder="Search organisations..."
        className={isSelected ? "font-bold text-emerald-600" : ""}
      />
      {searchQuery.length >= 2 && searchResults.length === 0 && !isLoading && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          <div className="p-2 text-gray-500">No results found</div>
        </div>
      )}
      {showDropdown && searchQuery.length >= 2 && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
          {searchResults.map((org) => (
            <div
              key={`${org.type}-${org.id}`}
              className="p-2 hover:bg-gray-100 cursor-pointer"
              onClick={() => handleSelectOrganisation(org)}
            >
              <div className="font-medium">{org.name}</div>
              <div className="text-sm text-gray-500">
                {[org.town, org.country].filter(Boolean).join(", ")}
                {(org.town || org.country) && " • "}
                {org.type}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default ControlledSearch;
