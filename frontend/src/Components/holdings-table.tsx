"use client"

import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {HoldingType} from "@/types/types.tsx"; // Adjust the import based on your project structure

const DataTable = ({ holdings }: { holdings: HoldingType[] }) => {
  return (
      <Table className="table-container">
        <TableHeader>
          <TableRow>
            <TableHead>Symbol</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Quantity</TableHead>
            <TableHead>Market Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {holdings.map((row, index) => (
              <TableRow key={index}>
                <TableCell>{row.symbol}</TableCell>
                <TableCell>{row.side}</TableCell>
                <TableCell>{row.quantity}</TableCell>
                <TableCell>${row.market_value}</TableCell>
              </TableRow>
          ))}
        </TableBody>
      </Table>
  );
};

export default DataTable;