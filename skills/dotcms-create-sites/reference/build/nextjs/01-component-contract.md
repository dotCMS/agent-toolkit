# 01 · The contract: content type variable = component key

The headless counterpart to VTL's "choose the mechanism" step
([vtl/01](../vtl/01-choose-mechanism.md)). In VTL you pick *where the markup lives* —
container `<Var>.vtl`, widget `widgetCode`, or detail-page VTL. In headless there is
one answer for everything: **every content type that can appear on a page needs a React
component**, and the map key is what connects them.

This is the join between the two halves of the build, and the usual cause of a slot
rendering as "no component":

```ts
export const pageComponents = {
  Book: BookCard,        // key === the content type's Velocity variable in dotCMS
  webPageContent: WebPageContent,
};
```

Keys are **case-exact** and must equal the content type's variable name — the same
value `core/02` warns you to check against the reserved-name list. Because of this,
create and name the content type *before* writing its component.

Rules and lazy-loading: **@dotcms/react README → Component Mapping**.
