/*
 * Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT.
 */

import { rootGetWelcomeMessage } from "../funcs/rootGetWelcomeMessage.js";
import { ClientSDK, RequestOptions } from "../lib/sdks.js";
import { unwrapAsync } from "../types/fp.js";

export class Root extends ClientSDK {
  /**
   * Root endpoint
   *
   * @remarks
   * Welcome to the Racing Drivers API
   */
  async getWelcomeMessage(
    options?: RequestOptions,
  ): Promise<any> {
    return unwrapAsync(rootGetWelcomeMessage(
      this,
      options,
    ));
  }
}
