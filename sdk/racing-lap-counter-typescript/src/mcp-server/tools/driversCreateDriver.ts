/*
 * Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT.
 */

import { driversCreateDriver } from "../../funcs/driversCreateDriver.js";
import * as components from "../../models/components/index.js";
import { formatResult, ToolDefinition } from "../tools.js";

const args = {
  request: components.DriverCreate$inboundSchema,
};

export const tool$driversCreateDriver: ToolDefinition<typeof args> = {
  name: "drivers-create-driver",
  description: `Create a new driver

Create a new racing driver in the database`,
  args,
  tool: async (client, args, ctx) => {
    const [result, apiCall] = await driversCreateDriver(
      client,
      args.request,
      { fetchOptions: { signal: ctx.signal } },
    ).$inspect();

    if (!result.ok) {
      return {
        content: [{ type: "text", text: result.error.message }],
        isError: true,
      };
    }

    const value = result.value;

    return formatResult(value, apiCall);
  },
};
