import React from "react";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import { Button } from "@material-tailwind/react";
import { PiExportBold } from "react-icons/pi";
import { ITableRow } from "../../utils/types";

interface IExcelExport {
    data: ITableRow[];
    fileName: string;
}

const ExcelExport: React.FC<IExcelExport> = ({ data, fileName }) => {
    const exportToExcel = () => {
        const worksheet = XLSX.utils.json_to_sheet(data);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
        const excelBuffer = XLSX.write(workbook, {
            bookType: "xlsx",
            type: "array",
        });
        const blob = new Blob([excelBuffer], {
            type: "application/octet-stream",
        });
        saveAs(blob, `${fileName}.xlsx`);
    };
    return (
        <div className="flex w-full shrink-0 gap-2 md:w-max">
            <Button
                size="sm"
                variant="filled"
                className="flex hover:bg-text_primary/90  bg-text_primary items-center gap-3"
                onClick={exportToExcel}
            >
                <PiExportBold size={16} />
                Export Data to Excel
            </Button>
        </div>
    );
};

export default ExcelExport;
