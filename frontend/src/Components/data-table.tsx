"use client"

import * as React from "react";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {ActionType} from "@/types/types.tsx"; // Adjust the import based on your project structure

const DataTable = ({ actions }: { actions: ActionType[] }) => {
  return (
      <Table className="table-container">
        <TableHeader>
          <TableRow>
            <TableHead>Activity Type</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Net Amount</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {actions.map((row, index) => (
              <TableRow key={index}>
                <TableCell>{row.activity_type}</TableCell>
                <TableCell>{row.date}</TableCell>
                <TableCell>{row.net_amount}</TableCell>
                <TableCell>{row.status}</TableCell>
              </TableRow>
          ))}
        </TableBody>
      </Table>
  );
};

export default DataTable;