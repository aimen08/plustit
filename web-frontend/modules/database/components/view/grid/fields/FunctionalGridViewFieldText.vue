<template functional>
  <div ref="cell" dir="auto" class="grid-view__cell" :class="data.staticClass || ''">
    <div class="grid-field-text">{{ props.value }}</div>
  </div>
</template>
